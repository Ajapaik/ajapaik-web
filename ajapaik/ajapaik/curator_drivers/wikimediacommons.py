import sys
from json import dumps, loads
from requests import get


import flickrapi
from django.conf import settings
from math import ceil
from django.utils.html import strip_tags
from ajapaik.ajapaik.models import Photo, AlbumPhoto, Album
from django.utils.html import strip_tags


class CommonsDriver(object):
    def __init__(self):
        self.search_url = 'https://commons.wikimedia.org/w/api.php'
        self.page_size = 20

    def search(self, cleaned_data):
        return loads(get(self.search_url, {
            'format':'json',
            'action':'query',
            'list':'search',
            'srnamespace':'6',
            'srsearch':cleaned_data['fullSearch'],
            'srlimit':self.page_size,
            'sroffset':self.page_size*cleaned_data['flickrPage']
        }).text)


    @staticmethod
    def transform_response(response, remove_existing=False, current_page=1):
        ids = None
        page_count = 0
        page_size=20
        if 'query' in response:
            if 'search' in response['query']:
                ids = [p['pageid'] for p in response['query']['search']]
            if 'searchinfo' in response['query'] and 'totalhits' in response['query']['searchinfo']:
                totalhits=response['query']['searchinfo']['totalhits']
                page_count = int(ceil(float(totalhits) / float(page_size)))

        transformed = {
            'result': {
                'firstRecordViews': [],
                'page': current_page,
                'pages': page_count
            }
        }
        if not ids:
            return dumps(transformed)

        ok=1

        existing_photos = Photo.objects.filter(source__description='Wikimedia Commons', external_id__in=ids).all()
        for p in response['query']['search']:
            existing_photo = existing_photos.filter(external_id=p['pageid']).first()
            if remove_existing and existing_photo:
                print("continue", file=sys.stderr)
                continue
            else:
                url='https://commons.wikimedia.org/w/api.php'
                imageinfo=get(url, {
                    'action':'query',
                    'format':'json',
                    'titles': p['title'],
                    'prop': 'imageinfo|coordinates',
                    'iiprop': 'extmetadata|url|parsedcomment',
                    'iiurlwidth': 500,
                    'iiurlheight': 500,
                    'iiextmetadatamultilang':1
                }).json()

                title=p['title'].replace('File:', '').replace('Tiedosto:', '').replace('_', ' ').replace('.JPG', '').replace('.jpg', '')

                author=""
                description=None
                date_str=""
                uploader=""
                latitude=None
                longitude=None

                targetlangs=['et', 'fi', 'en', 'sv', 'no']

                if 'query' in imageinfo and 'pages' in imageinfo['query']:
                    for pageid in imageinfo['query']['pages']:
                        pp=imageinfo['query']['pages'][pageid]

                        if 'imageinfo' in pp:
                            im=pp['imageinfo'][0]

                            if 'ObjectName' in im:
                                title=im['ObjectName']['value']

                            if 'thumburl' in im:
                                thumbnailUrl=im['thumburl']
                            if 'url' in im:
                                imageUrl=im['url']

                            if 'descriptionurl' in im:
                                recordUrl=im['descriptionurl']

                            if 'extmetadata' in im:
                                em=im['extmetadata']
                                if 'Artist' in em:
                                    author=strip_tags(em['Artist']['value']).strip()
                                if 'LicenseShortName' in em:
                                    licence=strip_tags(em['LicenseShortName']['value']).strip()
                                if 'Credit' in em:
                                    credit=strip_tags(em['Credit']['value']).strip()
                                if 'DateTimeOriginal' in em:
                                    date=strip_tags(em['DateTimeOriginal']['value']).strip()
                                if 'ImageDescription' in em and em['ImageDescription']['value']:
                                    desclangs=em['ImageDescription']['value']
                                    if isinstance(desclangs, str):
                                        description=strip_tags(desclangs).strip()
                                    else:
                                        for lang in desclangs:
                                            description=strip_tags(desclangs[lang]).strip()
                                            if lang in targetlangs:
                                                break

                                if 'GPSLatitude' in em and 'GPSLongitude' in em:
                                    latitude=em['GPSLatitude']['value']
                                    longitude=em['GPSLongitude']['value']

                        try:
                            transformed_item = {
                                'isCommonsResult': True,
                                'cachedThumbnailUrl': thumbnailUrl or None,
                                'title': title,
                                'institution': 'Wikimedia Commons',
                                'imageUrl': imageUrl,
                                'id': p['pageid'],
                                'mediaId': p['pageid'],
                                'identifyingNumber': p['pageid'],
                                'urlToRecord': recordUrl,
                                'latitude': latitude,
                                'longitude': longitude,
                                'creators':author,
                                'description': description,
                                'licence': licence
                            }
                        except:
                            print("Skipping: " + p.title, file=sys.stderr)
                            continue

                        if existing_photo:
                            transformed_item['ajapaikId'] = existing_photo.id
                            album_ids = AlbumPhoto.objects.filter(photo=existing_photo).values_list('album_id', flat=True)
                            transformed_item['albums'] = Album.objects.filter(pk__in=album_ids, atype=Album.CURATED) \
                                .values_list('id', 'name')

                        print(transformed_item, file=sys.stderr)
                        transformed['result']['firstRecordViews'].append(transformed_item)

        transformed = dumps(transformed)
        return transformed
