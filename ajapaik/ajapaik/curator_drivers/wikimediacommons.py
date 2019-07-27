import sys, re
import flickrapi
from django.conf import settings
from math import ceil
from django.utils.html import strip_tags
from ajapaik.ajapaik.models import Photo, AlbumPhoto, Album
from django.utils.html import strip_tags
from json import dumps, loads
from requests import get

class CommonsDriver(object):
    def __init__(self):
        self.search_url = 'https://commons.wikimedia.org/w/api.php'
        self.page_size = 20

    def search(self, cleaned_data):
        page_count = 0
        total_hits = 0
        titles = []
        petscan_url=""

        if cleaned_data['fullSearch'].strip().startswith('https://petscan.wmflabs.org/'):
            petscan_url=cleaned_data['fullSearch'].strip() + "&format=json"
        elif cleaned_data['fullSearch'].strip().startswith('https://commons.wikimedia.org/wiki/Category:'):
            target=re.search('https://commons.wikimedia.org/wiki/Category:(.*?)(\?|\#|$)',cleaned_data['fullSearch']).group(1)
            petscan_url="https://petscan.wmflabs.org/?psid=10268672&format=json&categories=" +target;
            print(petscan_url)
        elif cleaned_data['fullSearch'].strip().startswith('https://commons.wikimedia.org/wiki/'):
            target=re.search('https://commons.wikimedia.org/wiki/(.*?)(\?|\#|$)',cleaned_data['fullSearch']).group(1)
            petscan_url="https://petscan.wmflabs.org/?psid=10268672&format=json&outlinks_yes=" +target;
            print(petscan_url)

        if petscan_url!="":
            json=loads(get(petscan_url, {}).text)

            n=0
            offset=self.page_size*(cleaned_data['flickrPage']-1)
            if '*' in json and json['*'][0] and 'a' in json['*'][0] and '*' in json['*'][0]['a']:
                for p in json['*'][0]['a']['*']:
                    if p['nstext']=="File":
                        if (n>=offset and  n<(offset + self.page_size)): 
                            titles.append("File:" + p['title'].strip() )
                        n=n+1

            page_count = int(ceil(float(n) / float(self.page_size)))

        else:
            json=loads(get(self.search_url, {
                'format':'json',
                'action':'query',
                'list':'search',
                'srnamespace':'6',
                'srsearch':cleaned_data['fullSearch'],
                'srlimit':self.page_size,
                'sroffset':self.page_size*(cleaned_data['flickrPage']-1)
            }).text)

            if 'query' in json:
                if 'search' in json['query']:
                    titles = [p['title'] for p in json['query']['search']]

                if 'searchinfo' in json['query'] and 'totalhits' in json['query']['searchinfo']:
                    totalhits=json['query']['searchinfo']['totalhits']
                    page_count = int(ceil(float(totalhits) / float(self.page_size)))

        response= {
            'titles': titles,
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

        titles='|'.join(response['titles'])

        nn=0
        if response['titles']:
            if 1:
                url='https://commons.wikimedia.org/w/api.php'
                imageinfo=get(url, {
                    'action':'query',
                    'format':'json',
                    'titles': titles,
                    'prop': 'imageinfo|coordinates',
                    'iiprop': 'extmetadata|url|parsedcomment',
                    'iiurlwidth': 500,
                    'iiurlheight': 500,
                    'iiextmetadatamultilang':1
                })
                print(imageinfo.text)
                imageinfo=imageinfo.json()


                targetlangs=['et', 'fi', 'en', 'sv', 'no']
                if 'query' in imageinfo and 'pages' in imageinfo['query']:
                    for pageid in imageinfo['query']['pages']:

                        # p['page_id'] maybe from another wiki, so we need to get Wikimedia Commons page_id from imageinfo.
                        existing_photo =  Photo.objects.filter(external_id=pageid, source__description='Wikimedia Commons').first()
                        if remove_existing and existing_photo:
                            print("continue", file=sys.stderr)
                            continue

                        nn=nn+1
                        title=""
                        author=""
                        description=None
                        date_str=""
                        uploader=""
                        latitude=None
                        longitude=None

                        pp=imageinfo['query']['pages'][pageid]
                        if 'title' in pp:
                            title=pp['title']

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
                                if 'LicenseUrl' in em:
                                    licenceUrl=strip_tags(em['LicenseUrl']['value']).strip()
                                if 'UsageTerms' in em:
                                    licenceDesc=strip_tags(em['UsageTerms']['value']).strip()
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

                                if description and description!=title and not title in description:
                                    title=title + " - " + description

                        if not author or author =="":
                            continue

                        if not credit or credit =="":
                            continue

                        if not licence or licence =="":
                            continue

                        if not licenceDesc or licenceDesc =="":
                            continue

                        if not title or title =="":
                            continue

                        try:
                            transformed_item = {
                                'isCommonsResult': True,
                                'cachedThumbnailUrl': thumbnailUrl or None,
                                'title': title,
                                'institution': 'Wikimedia Commons',
                                'imageUrl': imageUrl,
                                'id': pageid,
                                'mediaId': pageid,
                                'identifyingNumber': pageid,
                                'urlToRecord': recordUrl,
                                'latitude': latitude,
                                'longitude': longitude,
                                'creators':author,
                                'description': description,
                                'licence': licenceDesc,
                                'licenceUrl': licenceUrl
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

        print(nn, " photos found") 
        transformed = dumps(transformed)
        return transformed
