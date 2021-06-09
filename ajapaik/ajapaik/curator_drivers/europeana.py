import re
import sys
import urllib.parse
from json import dumps, loads
from math import ceil

from django.conf import settings
from requests import get, head

from ajapaik.ajapaik.models import Photo, AlbumPhoto, Album


def _filter_out_url(str):
    return 'http' not in str

class EuropeanaDriver(object):
    def __init__(self):
        self.search_url = 'https://www.europeana.eu/api/v2/search.json'
        self.page_size = 20

    def urlToResponseTitles(self, url):
        response = {
            'titles': [],
            'pages': 0
        }

        url = re.search('https://[^.]*?\.europeana.eu/.*?/.*?(record.*?)(\.json|.html)?(\?|#|$)', url).group(1)
        json_url = 'https://www.europeana.eu/api/v2/' + url + '.json'
        record_url = 'https://www.europeana.eu/portal/' + url + '.html'
        json = loads(get(json_url, {'wskey': settings.EUROPEANA_API_KEY}).text)

        print(json_url)

        latitude = None
        longitude = None
        imageUrl = None
        title = None
        id = None
        description = None
        authors = ''

        if 'object' in json and 'aggregations' in json['object']:
            d = json['object']
            a = d['aggregations'][0]
            p = d['proxies']
            id = re.search('record(/.*?/.*?)$', url).group(1)
            if not id:
                return response

            if 'edmIsShownBy' in a:
                imageUrl = a['edmIsShownBy'] or None

            for pp in p:
                if 'dcTitle' in pp:
                    title = pp['dcTitle']

                if 'edmPlaceLatitude' in pp and latitude is None:
                    latitude = pp['edmPlaceLatitude']
                if 'edmPlaceLongitude' in pp and longitude is None:
                    longitude = pp['edmPlaceLongitude']

                if 'dcDescription' in pp:
                    description = pp['dcDescription']

                if 'dcCreator' in pp:
                    if 'http' not in ', '.join(pp['dcCreator']['def']):
                        authors = pp['dcCreator']

            if 'places' in d:
                for place in d['places']:
                    if 'latitude' in place and latitude is None:
                        latitude = [place['latitude']]
                    if 'longitude' in place and longitude is None:
                        longitude = [place['longitude']]

            if not authors and 'agents' in d:
                for agent in d['agents']:
                    if 'prefLabel' in agent:
                        authors = agent['prefLabel']
                        break

            res = {
                'rights': a['edmRights']['def'],
                'dcTitleLangAware': title,
                'dcDescriptionLangAware': description,
                'edmAgentLabelLangAware': authors,
                'edmIsShownBy': [imageUrl],
                'edmPreview': [imageUrl],
                'dataProvider': a['edmDataProvider']['def'],
                'edmPlaceLatitude': latitude,
                'edmPlaceLongitude': longitude,
                'title': title,
                'id': id,
                'guid': record_url

            }
            print(res)
            response['titles'].append(res)
            response['pages'] = 1

        print(json)
        print('---------------')
        print(response)
        return response

    def search(self, cleaned_data):
        titles = []

        response = {
            'titles': titles,
            'pages': 0
        }

        if cleaned_data['fullSearch'].strip().startswith('https://www.europeana.eu/portal/'):
            target_url = re.search('(https://[^.]*?\.europeana.eu/.*?/.*?record.*?)\.(json|html)(\?|#|$)',
                                   cleaned_data['fullSearch']).group(1)

            response = self.urlToResponseTitles(target_url)
            print(target_url)

        else:
            params = {
                'wskey': settings.EUROPEANA_API_KEY,
                'thumbnail': 'true',
                'media': 'true',
                'reusability': 'open',
                'profile': 'portal',
                'qf': 'TYPE:"IMAGE"',
                'query': cleaned_data['fullSearch'],
                'rows': self.page_size,
                'start': self.page_size * (cleaned_data['flickrPage'] - 1) + 1
            }
            json = loads(get(self.search_url, params).text)

            if 'totalResults' in json:
                page_count = int(ceil(float(json['totalResults']) / float(self.page_size)))
                response = {
                    'titles': json['items'],
                    'pages': page_count
                }
        return response

    @staticmethod
    def transform_response(response, remove_existing=False, current_page=1):
        transformed = {
            'result': {
                'firstRecordViews': [],
                'page': current_page,
                'pages': response['pages']
            }
        }
        for p in response['titles']:
            date, author, title = None, None, None

            print(p, file=sys.stderr)

            licence_desc = p['rights'][0] or None
            licence_url = p['rights'][0] or None
            institution = p['dataProvider'][0] or p['provider'][0] or None
            titlelangs = ['def', 'en', 'fi', 'ee', 'se']

            if 'date' in p:
                date = p['date']

            title = ''
            description = ''

            if 'dcDescriptionLangAware' in p:
                prefix = ''
                for lang in titlelangs:
                    if lang in p['dcDescriptionLangAware'] and p['dcDescriptionLangAware']:
                        for desc in p['dcDescriptionLangAware'][lang]:
                            if len(desc) > 3 and desc not in description:
                                description += prefix + desc
                                prefix = ' - '
                        break

            if 'dcTitleLangAware' in p:
                prefix = ''
                for lang in titlelangs:
                    if lang in p['dcTitleLangAware']:
                        for titledesc in p['dcTitleLangAware'][lang]:
                            if len(titledesc) > 3 and titledesc not in description and titledesc not in title:
                                title += prefix + titledesc
                                prefix = ' - '
                        break

            if title != '' and title not in description:
                title = title + ' - ' + description
            elif title == '':
                title = description

            if ('title' in p and (not title or title == '')):
                if isinstance(p['title'], list):
                    title = ', '.join(set(p['title']))
                elif isinstance(p['title'], dict):
                    title = ', '.join(set(p['title']))
                else:
                    title = p['title'].strip()

            if len(title) > 400:
                t = re.search('\A(.*?\n.*?)\n', title, re.MULTILINE)
                if t:
                    title = t.group(1)

            if len(title) > 400:
                t = re.search('\A(.*?)\n', title, re.MULTILINE)
                if t:
                    title = t.group(1)

            if 'dcCreatorLangAware' in p:
                for lang in p['dcCreatorLangAware']:
                    author = ', '.join(filter(_filter_out_url, set(p['dcCreatorLangAware'][lang])))
            elif 'edmAgentLabelLangAware' in p:
                for lang in p['edmAgentLabelLangAware']:
                    author = ', '.join(set(p['edmAgentLabelLangAware'][lang]))

            if 'edmIsShownBy' in p:
                for url in p['edmIsShownBy']:
                    if '.tif' not in url:
                        imageUrl = url
                        thumbnailUrl = url
                        break

            if 'edmPreview' in p:
                for url in p['edmPreview']:
                    if '.tif' not in url:
                        thumbnailUrl = url
                        url = re.search('thumbnail-by-url.json.*?uri=(.*?.jpe?g)', url, re.IGNORECASE)
                        if url:
                            imageUrl = urllib.parse.unquote(url.group(1))
                        break

            latitude = p.get('edmPlaceLatitude') or None
            longitude = p.get('edmPlaceLongitude') or None

            if latitude:
                latitude = latitude[0]
            if longitude:
                longitude = longitude[0]

            if not imageUrl or imageUrl == '':
                continue
            if not licence_url or licence_url == '':
                continue
            if not licence_desc or licence_desc == '':
                continue
            if not title or title == '':
                continue

            transformed_item = {
                'isEuropeanaResult': True,
                'cachedThumbnailUrl': thumbnailUrl,
                'title': title,
                'institution': 'Europeana / ' + institution,
                'imageUrl': imageUrl,
                'id': p['id'],
                'mediaId': p['id'],
                'identifyingNumber': p['id'],
                'urlToRecord': p['guid'].split('?')[0],
                'latitude': latitude,
                'longitude': longitude,
                'creators': author,
                'description': title,
                'licence': licence_desc,
                'licenceUrl': licence_url,
                'date': date
            }

            print('DEBUG\n' + p['id'] + '\n' + institution)
            # External will break when saving the photo
            existing_photo = Photo.objects.filter(external_id=p['id'],
                                                  source__description=transformed_item['institution']).first()
            if remove_existing and existing_photo:
                print('remove existing', file=sys.stderr)
                continue

            existing_photo = Photo.objects.filter(source_key=p['id'],
                                                  source__description=transformed_item['institution']).first()
            if remove_existing and existing_photo:
                print('remove existing', file=sys.stderr)
                continue

            existing_photo = Photo.objects.filter(source_url=transformed_item['urlToRecord']).first()
            if remove_existing and existing_photo:
                print('remove existing', file=sys.stderr)
                continue

            if existing_photo:
                transformed_item['ajapaikId'] = existing_photo.id
                album_ids = AlbumPhoto.objects.filter(photo=existing_photo).values_list('album_id', flat=True)
                transformed_item['albums'] = list(Album.objects.filter(pk__in=album_ids, atype=Album.CURATED)
                                                  .values_list('id', 'name').distinct())

            print(transformed_item, file=sys.stderr)
            transformed['result']['firstRecordViews'].append(transformed_item)

        transformed = dumps(transformed)
        return transformed
