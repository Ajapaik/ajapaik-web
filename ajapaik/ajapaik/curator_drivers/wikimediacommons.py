import re
import sys
import urllib.parse
from json import dumps, loads
from math import ceil

from django.utils.html import strip_tags
from requests import get

from ajapaik.ajapaik.models import Photo, AlbumPhoto, Album


def wikimediacommons_find_photo_by_url(record_url, profile):
    photo = None
    filename = re.search(r'https://commons.wikimedia.org/wiki/File:(.*?)(\?|\#|$)', record_url, re.IGNORECASE)
    if filename:
        filename = filename.group(1)
        file_url = f'https://commons.wikimedia.org/wiki/File:{filename}'
        photo = Photo.objects.filter(source_url=file_url, source__description='Wikimedia Commons').first()

    return photo


class CommonsDriver(object):
    def __init__(self):
        self.search_url = 'https://commons.wikimedia.org/w/api.php'
        self.page_size = 20

    def search(self, cleaned_data):
        page_count = 0
        titles = []
        petscan_url = ''
        outlinks_page = ''

        if cleaned_data['fullSearch'].strip().replace('http://', 'https://', ).startswith(
                'https://petscan.wmflabs.org/'):
            petscan_url = f'{cleaned_data["fullSearch"].strip()}&format=json'
        elif cleaned_data['fullSearch'].strip().replace('http://', 'https://').startswith(
                'https://commons.wikimedia.org/wiki/Category:'):
            target = re.search(r'https://commons.wikimedia.org/wiki/Category:(.*?)(\?|\#|$)',
                               cleaned_data['fullSearch']).group(1)
            petscan_url = f'https://petscan.wmflabs.org/?psid=10268672&format=json&categories={target}'
            print(petscan_url)
        elif cleaned_data['fullSearch'].strip().startswith('https://commons.wikimedia.org/wiki/'):
            target = re.search(r'https://commons.wikimedia.org/wiki/(.*?)(\?|#|$)', cleaned_data['fullSearch']).group(1)
            petscan_url = f'https://petscan.wmflabs.org/?psid=10268672&format=json&outlinks_yes={target}'
            outlinks_page = target
            print(petscan_url)

        if petscan_url != '':
            titles_all = []
            json = loads(get(petscan_url, {}).text)

            n = 0
            offset = self.page_size * (cleaned_data['driverPage'] - 1)
            if '*' in json and json['*'][0] and 'a' in json['*'][0] and '*' in json['*'][0]['a']:
                for p in json['*'][0]['a']['*']:
                    if p['nstext'] == 'File':
                        titles_all.append(f'File:{p["title"].strip()}')

            # Failback. Read imagelinks from html
            if outlinks_page != '':
                url = f'https://commons.wikimedia.org/wiki/{outlinks_page}'
                html = get(url, {}).text
                urls = re.findall(r'(file:.*?\.jpe?g)\'', html, re.IGNORECASE)
                for u in urls:
                    u = urllib.parse.unquote(u)
                    if u not in titles_all:
                        titles_all.append(u)

            # set seek and limit
            for t in titles_all:
                if offset <= n < (offset + self.page_size):
                    titles.append(t)
                n = n + 1

            page_count = int(ceil(float(len(titles_all)) / float(self.page_size)))

        else:
            json = loads(get(self.search_url, {
                'format': 'json',
                'action': 'query',
                'list': 'search',
                'srnamespace': '6',
                'srsearch': cleaned_data['fullSearch'],
                'srlimit': self.page_size,
                'sroffset': self.page_size * (cleaned_data['driverPage'] - 1)
            }).text)

            if 'query' in json:
                if 'search' in json['query']:
                    titles = [p['title'] for p in json['query']['search']]

                if 'searchinfo' in json['query'] and 'totalhits' in json['query']['searchinfo']:
                    totalhits = json['query']['searchinfo']['totalhits']
                    page_count = int(ceil(float(totalhits) / float(self.page_size)))

        response = {
            'titles': titles,
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

        titles = '|'.join(response['titles'])

        nn = 0
        if response['titles']:
            url = 'https://commons.wikimedia.org/w/api.php'
            imageinfo = get(url, {
                'action': 'query',
                'format': 'json',
                'titles': titles,
                'prop': 'imageinfo|coordinates',
                'iiprop': 'extmetadata|url|parsedcomment|mime|dimensions',
                'iiurlwidth': 500,
                'iiurlheight': 500,
                'iiextmetadatamultilang': 1
            })
            #                print(imageinfo.text)
            imageinfo = imageinfo.json()

            targetlangs = ['et', 'fi', 'en', 'sv', 'no']
            if 'query' in imageinfo and 'pages' in imageinfo['query']:
                for pageid in imageinfo['query']['pages']:
                    existing_photo = Photo.objects.filter(external_id=pageid,
                                                          source__description='Wikimedia Commons'
                                                          ).first()
                    if remove_existing and existing_photo:
                        print('continue', file=sys.stderr)
                        continue

                    nn = nn + 1
                    title = ''
                    author = ''
                    description = None
                    date = ''
                    latitude = None
                    longitude = None
                    licence = ''
                    licence_desc = ''
                    licenceUrl = ''
                    record_url = ''
                    thumbnail_url = None
                    credit = ''

                    pp = imageinfo['query']['pages'][pageid]
                    if 'title' in pp:
                        title = pp['title']

                    if 'imageinfo' in pp:
                        im = pp['imageinfo'][0]

                        if 'thumburl' in im:
                            thumbnail_url = im['thumburl']

                        allowed_mime_types = ['image/jpeg', 'image/png', 'image/gif']
                        if 'mime' in im and im['mime'] in allowed_mime_types:
                            if 'url' in im:
                                imageUrl = im['url']
                        else:
                            imageUrl = thumbnail_url.replace('-500px-', f'-{str(im["width"])}px-')

                        if 'descriptionurl' in im:
                            record_url = im['descriptionurl']

                        if 'extmetadata' in im:
                            em = im['extmetadata']

                            if 'ObjectName' in em:
                                title = strip_tags(em['ObjectName']['value']).strip()
                            if 'Artist' in em:
                                authors = em['Artist']['value']
                                if isinstance(authors, dict) or isinstance(authors, list):
                                    for lang in authors:
                                        author = strip_tags(authors[lang]).strip()
                                        if lang in targetlangs:
                                            break
                                else:
                                    author = strip_tags(authors).strip()
                            if 'LicenseShortName' in em:
                                licence = strip_tags(em['LicenseShortName']['value']).strip()
                            if 'LicenseUrl' in em:
                                licenceUrl = strip_tags(em['LicenseUrl']['value']).strip()
                            if 'UsageTerms' in em:
                                licence_desc = strip_tags(em['UsageTerms']['value']).strip()
                            if 'Credit' in em:
                                credit = strip_tags(em['Credit']['value']).strip()
                            if 'DateTimeOriginal' in em:
                                date = str(em['DateTimeOriginal']['value'])
                                date = re.sub('<div.*?</div>', '', date)
                                date = strip_tags(date).strip()

                            if 'ImageDescription' in em and em['ImageDescription']['value']:
                                desclangs = em['ImageDescription']['value']
                                if isinstance(desclangs, dict) or isinstance(desclangs, list):
                                    for lang in desclangs:
                                        description = strip_tags(desclangs[lang]).strip()
                                        if lang in targetlangs:
                                            break
                                else:
                                    description = strip_tags(desclangs).strip()

                            if 'GPSLatitude' in em and 'GPSLongitude' in em:
                                latitude = em['GPSLatitude']['value']
                                longitude = em['GPSLongitude']['value']

                            if description and description != title and title not in description:
                                title = f'{title} - {description}'

                    if not author or author == '':
                        continue

                    if not credit or credit == '':
                        continue

                    if not licence or licence == '':
                        continue

                    if not licence_desc or licence_desc == '':
                        continue

                    if not title or title == '':
                        continue

                    try:
                        transformed_item = {
                            'isCommonsResult': True,
                            'cachedThumbnailUrl': thumbnail_url or None,
                            'title': title,
                            'institution': 'Wikimedia Commons',
                            'imageUrl': imageUrl,
                            'id': pageid,
                            'mediaId': pageid,
                            'identifyingNumber': pageid,
                            'urlToRecord': record_url,
                            'latitude': latitude,
                            'longitude': longitude,
                            'creators': author,
                            'description': description,
                            'licence': licence_desc,
                            'licenceUrl': licenceUrl,
                            'date': date
                        }
                    except:  # noqa
                        continue

                    if existing_photo:
                        transformed_item['ajapaikId'] = existing_photo.id
                        album_ids = AlbumPhoto.objects.filter(photo=existing_photo).values_list('album_id',
                                                                                                flat=True)
                        transformed_item['albums'] = list(
                            Album.objects.filter(pk__in=album_ids, atype=Album.CURATED).values_list('id',
                                                                                                    'name').distinct())

                    transformed['result']['firstRecordViews'].append(transformed_item)

        print(nn, 'photos found from wikimedia commons')
        transformed = dumps(transformed)
        return transformed
