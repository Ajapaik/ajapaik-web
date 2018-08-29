from json import dumps, loads
from math import ceil
from numpy import mean, median

from requests import get
import re
import sys
from time import sleep
import urllib2
from django.core.files.base import ContentFile
from project.ajapaik.models import Photo, AlbumPhoto, Album, GeoTag, Licence, Source
from django.contrib.gis.geos import GEOSGeometry, Point

def find_finna_photo_by_url(record_url, profile):
    print >>sys.stderr, ('find_finna_photo_by_url %s' % record_url)
    photo=None
    if re.search('(finna.fi|helsinkikuvia.fi)', record_url):
        print >>sys.stderr, ('find_finna_photo_by_url pre match')
        m = re.search('https:\/\/(hkm\.|www\.)?finna.fi\/Record\/(.*?)( |\?|#|$)', record_url) 
        if m:
            print >>sys.stderr, ('find_finna_photo_by_url first match')
            # Already in database?
            external_id=m.group(2) 
            photo = Photo.objects.filter(
                    external_id=external_id,
                ).first()

            # Import if not found
            if not photo:
                print >>sys.stderr, ('find_finna_photo_by_url second match')
                photo=import_finna_photo(external_id, profile)

    return photo


def import_finna_photo(id, profile):
    print >>sys.stderr, ('_importFinnaPhoto %s' % id) 

    record_url='https://api.finna.fi/v1/record'
    finna_result=get(record_url, {
        'id': id,
        'field[]': ['id', 'title', 'images', 'imageRights', 'authors', 'source', 'geoLocations', 'recordPage', 'year', 'summary', 'rawData'],
    })
    results=finna_result.json();
    p=results.get('records', None)

    print >>sys.stderr, ('_importFinnaPhoto00 save %s' % 'https://api.finna.fi/v1/record?id=' + id) 

    if p and p[0]:
        p=p[0]
        comma=", "

        institution=None
        if p['source']:
            if 'translated' in p['source'][0]:
                institution = p['source'][0]['translated']
            elif 'value' in p['source'][0]:
                institution = p['source'][0]['value']

        print >>sys.stderr, ('_importFinnaPhoto0a save %s' % id) 

        geography = None
        if 'geoLocations' in p:
            for each in p['geoLocations']:
                if 'POINT' in each:
                    point_parts = each.split(' ')
                    lon = point_parts[0][6:]
                    lat = point_parts[1][:-1]
                    p['longitude'] = lon
                    p['latitude'] = lat
                    geography=Point(x=float(lon), y=float(lat), srid=4326)
                    break

        print >>sys.stderr, ('_importFinnaPhoto0.1 save %s' % id) 

        licence = Licence.objects.get(pk=15) # 15 = unknown licence
        if 'imageRights' in p and 'copyright' in p['imageRights']:
            licence_str = p['imageRights']['copyright']
            if licence_str:
                licence = Licence.objects.get_or_create(name=licence)[0]
        print >>sys.stderr, ('_importFinnaPhoto0.2 save %s' % id) 

        authors=[]
        if 'authors' in p:
            if p['authors']['primary']:
                for k,each in p['authors']['primary'].items():
                    authors.append(k)

        source=None
        try:
            source = Source.objects.get(description=institution)
        except ObjectDoesNotExist:
            source = Source(
                         name=institution,
                         description=institution
                     )
            source.save()
        source = Source.objects.get(description=institution)
        print >>sys.stderr, ('_importFinnaPhoto0.3 save %s' % source) 

        external_id=p['id']        # muis_id
        external_sub_id=None       # muis_media_id
        if '_' in p['id']:
            external_id = p['id'].split('_')[0]
            external_sub_id = p["id"].split('_')[1]

        new_photo = Photo(
                        user=profile,
                        author=comma.join(authors),
                        description=p.get('title').rstrip().encode('utf-8') if p.get('title', None) else None,
                        source=source,
                        types=None,
                        keywords=None,
                        date_text=p.get('year').encode('utf-8') if p.get('year', None) else None,
                        licence=licence,
                        external_id=external_id,
                        external_sub_id=external_sub_id,
                        source_key=p.get('id', None),
                        source_url='https://www.finna.fi' + p.get('recordPage'),
                        geography=geography
                    )

        print >>sys.stderr, ('_importFinnaPhoto3.1a save %s' % source) 
        opener = urllib2.build_opener()
        print >>sys.stderr, ('_importFinnaPhoto3.2 save %s' % source) 
        opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36")]
        print >>sys.stderr, ('_importFinnaPhoto3.3 save %s' % source) 

        img_url='https://www.finna.fi' +  p['images'][0];
        img_response = opener.open(img_url)
        print >>sys.stderr, ('_importFinnaPhoto3.4 save %s' % img_url) 

        try:
            new_photo.image.save("finna.jpg", ContentFile(img_response.read()))
            print >>sys.stderr, ('_importFinnaPhoto3.5 save %s' % source) 
        except Exception as e:
            print >>sys.stderr, e.reason 

        print >>sys.stderr, ('_importFinnaPhoto5 save %s' % source) 
        new_photo.save()

        if p.get('latitude') and p.get('longitude') and not GeoTag.objects.filter(type=GeoTag.SOURCE_GEOTAG,
                                                     photo__source_key=new_photo.source_key).exists():
            source_geotag = GeoTag(
                lat=p.get('latitude'),
                lon=p.get('longitude'),
                origin=GeoTag.SOURCE,
                type=GeoTag.SOURCE_GEOTAG,
                map_type=GeoTag.NO_MAP,
                photo=new_photo,
                is_correct=True,
                trustworthiness=0.07,
                geography=geography
            )
            source_geotag.save()
            new_photo.latest_geotag = source_geotag.created
            new_photo.set_calculated_fields()

        new_photo.save()
        id=int(new_photo.id)
        photo = Photo.objects.filter(
                    pk=id
                ).first()

        print >>sys.stderr, ('_importFinnaPhoto6 save %d' % new_photo.id ) 
#        print >>sys.stderr, ('_importFinnaPhoto7 save %d' % photo.id ) 

        return photo


def safe_list_get(l, idx, default):
    try:
        return l[idx]
    except IndexError:
        return default


class FinnaDriver(object):
    def __init__(self):
        self.search_url = 'https://api.finna.fi/api/v1/search'
        self.page_size = 20

    def search(self, cleaned_data):
        return loads(get(self.search_url, {
            'lookfor': cleaned_data['fullSearch'],
            'type': 'AllFields',
            'page': cleaned_data['flickrPage'],
            'limit': self.page_size,
            'lng': 'en-gb',
            'field[]': ['id', 'title', 'images', 'imageRights', 'authors', 'source', 'geoLocations', 'recordPage',
                        'year', 'summary', 'rawData'],
            'filter[]': [
		'free_online_boolean:"1"',
		'~format:"0/Place/"',
		'~format:"0/Image/"',
		'~usage_rights_str_mv:"usage_B"',
	],

        }).text)

    def transform_response(self, response, remove_existing=False, finna_page=1):
        description2=""
        ids = [p['id'] for p in response['records']]
        page_count = int(ceil(float(response['resultCount']) / float(self.page_size)))
        transformed = {
            'result': {
                'firstRecordViews': [],
                'page': finna_page,
                'pages': page_count
            }
        }
        existing_photos = Photo.objects.filter(source__description='Finna', external_id__in=ids).all()
        for p in response['records']:
            existing_photo = existing_photos.filter(external_id=p['id']).first()
            if remove_existing and existing_photo or 'images' not in p:
                continue
            else:
                institution = 'Finna'
                if p['source']:
                    if 'translated' in p['source'][0]:
                        institution = p['source'][0]['translated']
                    elif 'value' in p['source'][0]:
                        institution = p['source'][0]['value']
                if 'geoLocations' in p:
                    for each in p['geoLocations']:
                        if 'POINT' in each:
                            point_parts = each.split(' ')
                            lon = point_parts[0][6:]
                            lat = point_parts[1][:-1]
                            p['longitude'] = lon
                            p['latitude'] = lat
                            break

#                if ('latitude' not in p or 'longitude' not in p) and 'rawData' in p and 'center_coords' in p['rawData']: 
#                    point_parts = p['rawData']['center_coords'].split(' ')
#                    lon = point_parts[0]
#                    lat = point_parts[1]
#                    p['longitude'] = lon
#                    p['latitude'] = lat

                licence = None
                if 'imageRights' in p and 'copyright' in p['imageRights']:
                    licence = p['imageRights']['copyright']

                authors=[]
                if 'authors' in p:
                    if p['authors']['primary']:
	                for k,each in p['authors']['primary'].items():
                            authors.append(k)

                transformed_item = {
                    'isFinnaResult': True,
                    'id': p['id'],
                    'mediaId': p['id'],
                    'identifyingNumber': p['id'],
                    'title': p['title'],
                    'institution': institution,
                    'date': p.get('year', None),
                    'cachedThumbnailUrl': 'https://www.finna.fi' + p['images'][0],
                    'imageUrl': 'https://www.finna.fi' + p['images'][0],
                    'urlToRecord': 'https://www.finna.fi' + p['recordPage'],
                    'latitude': p.get('latitude', None),
                    'longitude': p.get('longitude', None),
                    'creators': safe_list_get(authors,0, None),
                    'licence': licence,
                    'description': description2 or p.get('summary', None),
                }
                if existing_photo:
                    transformed_item['ajapaikId'] = existing_photo.id
                    album_ids = AlbumPhoto.objects.filter(photo=existing_photo).values_list('album_id', flat=True)
                    transformed_item['albums'] = Album.objects.filter(pk__in=album_ids, atype=Album.CURATED) \
                        .values_list('id', 'name')
                transformed['result']['firstRecordViews'].append(transformed_item)

        transformed = dumps(transformed)

        return transformed
