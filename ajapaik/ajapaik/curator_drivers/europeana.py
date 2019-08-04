import sys, re
import urllib.parse
from django.conf import settings
from math import ceil
from ajapaik.ajapaik.models import Photo, AlbumPhoto, Album
from django.utils.html import strip_tags
from json import dumps, loads
from requests import get

class EuropeanaDriver(object):
    def __init__(self):
        self.search_url = 'https://www.europeana.eu/api/v2/search.json'
        self.page_size = 20

    def urlToResponseTitles(self, url):
        url=re.search('(https://www.europeana.eu/portal/.*?record.*?)(\.json|.html)?(\?|\#|$)',url).group(1)
        json_url=url + ".json"
        json=loads(get(json_url, {}).text)

        latitude = None
        longitude = None
        imageUrl = None
        title = None
        id = None
        authors=""
        langs = ['en', 'fi', 'ee', 'se', 'def']

        response= {
            'titles': [],
            'pages': 0
        }

        if 'response' in json  \
            and 'document' in json['response']\
            and 'aggregations' in json['response']['document']:
            d=json['response']['document']
            a=json['response']['document']['aggregations'][0]
            p=json['response']['document']['proxies']
            places=json['response']['document']['places']
            id=re.search('record(\/.*?\/.*?)$',url).group(1)
            if not id:
                return response

            print(p)
            if 'edmIsShownBy' in a:
                imageUrl=a['edmIsShownBy'] or None

            for pp in p:
                if 'edmPlaceLatitude' in pp and latitude==None:
                    latitude = pp['edmPlaceLatitude']
                if 'edmPlaceLongitude' in pp and longitude==None:
                    longitude = pp['edmPlaceLongitude']
                if 'dcDescription' in pp and 'def' in pp['dcDescription']:
                    title =  pp['dcDescription']['def'][0]
                if 'dcDate' in pp and 'def' in pp['dcDate']:
                    date = pp['dcDate']['def'][0].replace("start=", "").replace(";end="," - ")

            if 'places' in d:
                for place in d['places']:
                    if 'latitude' in place and latitude==None:
                        latitude=[place['latitude']]
                    if 'longitude' in place and longitude==None:
                        longitude=[place['longitude']]

            if 'agents' in d:
                for agent in d['agents']:
                    if 'prefLabel' in agent and authors == "":
                        for l in langs:
                            if l in agent['prefLabel']:
                                authors=agent['prefLabel'][l]
                                break;

            title={
                'rights': a['edmRights']['def'],
                'dcTitleLangAware': {'def' : title },
                'edmAgentLabelLangAware': { 'def' : authors },
                'edmIsShownBy' : [imageUrl],
                'edmPreview': [imageUrl],
                'dataProvider': a['edmDataProvider']['def'],
                'edmPlaceLatitude': latitude,
                'edmPlaceLongitude': longitude,
                'title': title,
                'id': id,
                'guid': url + ".html"
 
            }
            response['titles'].append(title)
            response['pages']=1

        print(json)
        print("---------------")
        print(response)
        return response


    def search(self, cleaned_data):
        page_count = 0
        total_hits = 0
        titles = []
        petscan_url=""
        outlinks_page=""

        response= {
            'titles': titles,
            'pages': 0
        }

        if cleaned_data['fullSearch'].strip().startswith('https://www.europeana.eu/portal/'):
            target_url=re.search('(https://www.europeana.eu/portal/.*?record.*?)\.(json|html)(\?|\#|$)',cleaned_data['fullSearch']).group(1)

            response=self.urlToResponseTitles(target_url)
            print(target_url)

        else:
            params = {
                'wskey':settings.EUROPEANA_API_KEY,
                'thumbnail':'true',
                'media':'true',
                'reusability': 'open',
                'profile': 'portal',
                'qf':'',
                'theme': 'photography',
                'query':cleaned_data['fullSearch'],
                'rows':self.page_size,
                'start':self.page_size*(cleaned_data['flickrPage']-1)+1
            }
            json=loads(get(self.search_url, params).text)

            if 'totalResults' in json:
                page_count = int(ceil(float(json['totalResults']) / float(self.page_size)))
                response= {
                    'titles': json['items'],
                    'pages': page_count
                }
        return response

    @staticmethod
    def transform_response(response, remove_existing=False, current_page=1):
        ids = None

        transformed = {
            'result': {
                'firstRecordViews': [],
                'page': current_page,
                'pages': response['pages']
            }
        }
        for p in response['titles']:
            date, author, credit, licence, licenceDesc, title, thumbnailUrl, imageUrl, recordUrl = \
            None, None, None, None, None, None, None,None, None

            print(p, file=sys.stderr)

            try:
                licenceDesc = p['rights'][0] or None
                licenceUrl = p['rights'][0] or None
                institution = p['dataProvider'][0] or p['provider'][0] or None
                titlelangs = ['en', 'fi', 'ee', 'se', 'def']

                if 'date' in p:
                    date=p['date']

                if 'dcDescriptionLangAware' in p:
                    for lang in titlelangs:
                         if lang in p['dcDescriptionLangAware']:
                             title=p['dcDescriptionLangAware'][lang]

                if 'dcTitleLangAware' in p and title == None:
                    for lang in titlelangs:
                         if lang in p['dcTitleLangAware']:
                             title=p['dcTitleLangAware'][lang]

                if 'edmAgentLabelLangAware' in p:
                    for lang in p['edmAgentLabelLangAware']:
                        author=", ".join(p['edmAgentLabelLangAware'][lang])

                if 'edmIsShownBy' in p:
                    for url in p['edmIsShownBy']:
                       if not '.tif' in url:
                           imageUrl=url
                           thumbnailUrl=url
                           break

                if 'edmPreview' in p:
                    for url in p['edmPreview']:
                       if not '.tif' in url:
                           thumbnailUrl=url
                           break

                latitude = p.get('edmPlaceLatitude') or None
                longitude = p.get('edmPlaceLongitude') or None

                if latitude:
                    latitude=latitude[0]
                if longitude:
                    longitude=longitude[0]

                if not title or title == "":
                    if 'title' in p:
                        title=p['title'][0]

                if not imageUrl or imageUrl =="":
                    continue
                if not licenceUrl or licenceUrl =="":
                    continue
                if not licenceDesc or licenceDesc =="":
                    continue
                if not title or title =="":
                    continue

                transformed_item = {
                    'isEuropeanaResult': True,
                    'cachedThumbnailUrl': thumbnailUrl,
                    'title': title,
                    'institution': "Europeana / " + institution ,
                    'imageUrl': imageUrl,
                    'id': p['id'],
                    'mediaId': p['id'],
                    'identifyingNumber': p['id'],
                    'urlToRecord': p['guid'].split("?")[0],
                    'latitude': latitude,
                    'longitude': longitude,
                    'creators':author,
                    'description': title,
                    'licence': licenceDesc,
                    'licenceUrl': licenceUrl,
                    'date' : date
                }
            except:
                print("--------------\nSkipping: ", file=sys.stderr)
                print(p, file=sys.stderr)
                continue


            print("DEBUG\n" + p['id'] + "\n" + institution)
            # External will break when saving the photo
            existing_photo =  Photo.objects.filter(external_id=p['id'], source__description=transformed_item['institution']).first()
            if remove_existing and existing_photo:
                print("remove existing", file=sys.stderr)
                continue

            existing_photo =  Photo.objects.filter(source_key=p['id'], source__description=transformed_item['institution']).first()
            if remove_existing and existing_photo:
                print("remove existing", file=sys.stderr)
                continue

            existing_photo =  Photo.objects.filter(source_url=transformed_item['urlToRecord']).first()
            if remove_existing and existing_photo:
                print("remove existing", file=sys.stderr)
                continue


            if existing_photo:
                transformed_item['ajapaikId'] = existing_photo.id
                album_ids = AlbumPhoto.objects.filter(photo=existing_photo).values_list('album_id', flat=True)
                transformed_item['albums'] = list(Album.objects.filter(pk__in=album_ids, atype=Album.CURATED) \
                    .values_list('id', 'name').distinct())

            print(transformed_item, file=sys.stderr)
            transformed['result']['firstRecordViews'].append(transformed_item)

        transformed = dumps(transformed)
        return transformed
