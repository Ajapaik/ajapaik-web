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

    def search(self, cleaned_data):
        page_count = 0
        total_hits = 0
        titles = []
        petscan_url=""
        outlinks_page=""

        json=loads(get(self.search_url, {
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
        }).text)
#        print(json)
        response= {
            'titles': [],
            'pages': 0
        }


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
        date, author, credit, licence, licenceDesc, title, thumbnailUrl, imageUrl, recordUrl = \
        None, None, None, None, None, None, None,None, None

        transformed = {
            'result': {
                'firstRecordViews': [],
                'page': current_page,
                'pages': response['pages']
            }
        }
        for p in response['titles']:
            print(p, file=sys.stderr)

            try:

                print("a") 
                licenceDesc = p['rights'][0] or None
                licenceUrl = p['rights'][0] or None
                institution = p['dataProvider'][0] or p['provider'][0] or None
                titlelangs = ['en', 'fi', 'ee', 'se']

                if 'dcTitleLangAware' in p:
                    for lang in titlelangs:
                         if lang in p['dcTitleLangAware']:
                             title=p['dcTitleLangAware'][lang]

                if 'edmAgentLabelLangAware' in p:
                    for lang in p['edmAgentLabelLangAware']:
                        author=p['edmAgentLabelLangAware'][lang]

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
                    'latitude': p.get('edmPlaceLatitude',"") or None,
                    'longitude': p.get('edmPlaceLongitude',"") or None,
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

            existing_photo =  Photo.objects.filter(external_id=p['id'], source__description=institution).first()
            if remove_existing and existing_photo:
                print("remove existing", file=sys.stderr)
                continue


            if existing_photo:
                transformed_item['ajapaikId'] = existing_photo.id
                album_ids = AlbumPhoto.objects.filter(photo=existing_photo).values_list('album_id', flat=True)
                transformed_item['albums'] = Album.objects.filter(pk__in=album_ids, atype=Album.CURATED) \
                    .values_list('id', 'name')

            print(transformed_item, file=sys.stderr)
            transformed['result']['firstRecordViews'].append(transformed_item)

#        print(nn, " photos found") 
        transformed = dumps(transformed)
        return transformed
