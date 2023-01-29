import re
from json import dumps, loads
from math import ceil
from urllib.request import build_opener

from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.files.base import ContentFile
from requests import get

from ajapaik.ajapaik.models import Photo, AlbumPhoto, Album, GeoTag, Licence, Source, Profile


def finna_cut_title(title, short_title):
    if title is None:
        return None

    title = title.rstrip()
    if short_title and len(title) > 255:
        title = short_title.rstrip()
    return title[:255]


def finna_add_to_album(photo, target_album):
    if target_album and target_album != '':
        album = Album.objects.filter(name_en=target_album).first()

        if not album:
            album = Album.objects.create(name_en=target_album, atype=Album.CURATED, is_public=True, cover_photo=photo)

        if not AlbumPhoto.objects.filter(album=album, photo=photo).first():
            AlbumPhoto.objects.create(album=album, photo=photo)

        # update counts
        album.save()


def get_img_url(p, size=''):
    if 'imagesExtended' in p and len(p['imagesExtended']):
        if 'urls' in p['imagesExtended'][0]:
            sizes = [size, 'master', 'original', 'large', 'medium', 'small']
            for s in sizes:
                if s in p['imagesExtended'][0]['urls']:
                    if p['imagesExtended'][0]['urls'][s].startswith('/'):
                        return 'https://api.finna.fi' + p['imagesExtended'][0]['urls'][s]
                    else:
                        return p['imagesExtended'][0]['urls'][s]

    if 'images' in p and len(p['images']):
        return 'https://api.finna.fi' + p['images'][0]
    else:
        return None


def finna_find_photo_by_url(record_url, profile: Profile):
    photo = None
    if re.search('(finna.fi|helsinkikuvia.fi)', record_url):
        m = re.search(r'https://(hkm\.|www\.)?finna.fi/Record/(.*?)( |\?|#|$)', record_url)
        if m:
            # Already in database?
            external_id = m.group(2)
            # Detect old imports where ':' and '+' character is urlencoded
            external_id_urlencoded_1 = external_id.replace(':', '%3A')
            external_id_urlencoded_2 = external_id.replace('+', '%2B')
            external_id_urlencoded_3 = external_id_urlencoded_1.replace('+', '%2B')
            photo = Photo.objects.filter(
                external_id__in=[external_id, external_id_urlencoded_1, external_id_urlencoded_2,
                                 external_id_urlencoded_3],
            ).first()

            # Import if not found
            if not photo:
                photo = finna_import_photo(external_id, profile)

            m = re.search(r'hkm\.', record_url)

            if photo and m:
                finna_add_to_album(photo, 'Helsinki')
            elif photo:
                finna_add_to_album(photo, 'Finland')

    return photo


def finna_import_photo(record_id: int, profile: Profile):
    record_url = 'https://api.finna.fi/v1/record'
    finna_result = get(record_url, {
        'id': record_id,
        'field[]': ['id', 'title', 'shortTitle', 'images', 'imageRights', 'authors', 'source', 'geoLocations',
                    'recordPage', 'year',
                    'summary', 'rawData', 'imagesExtended'],
    })
    results = finna_result.json()
    p = results.get('records', None)

    if p and p[0]:
        p = p[0]
        comma = ', '

        if not len(p['images']):
            return None

        institution = None
        if p['source']:
            if 'translated' in p['source'][0]:
                institution = p['source'][0]['translated']
            elif 'value' in p['source'][0]:
                institution = p['source'][0]['value']

        geography = None
        if 'geoLocations' in p:
            for each in p['geoLocations']:
                if 'POINT' in each:
                    point_parts = each.split(' ')
                    lon = point_parts[0][6:]
                    lat = point_parts[1][:-1]
                    try:
                        p['longitude'] = float(lon)
                        p['latitude'] = float(lat)
                        geography = Point(x=float(lon), y=float(lat), srid=4326)
                        break
                    except Exception as e:
                        print(e)
                        continue

        title = p.get('title').rstrip()

        summary = ''
        if 'summary' in p:
            for each in p['summary']:
                if len(each.rstrip()) > len(summary):
                    summary = re.sub(
                        '--[^-]*?(filmi|paperi|negatiivi|digitaalinen|dng|dia|lasi|väri|tif|jpg|, mv)[^-]*?$', '',
                        each).rstrip()

        if title in summary:
            description = summary
        elif len(title) < 20:
            description = f'{title}; {summary}'
        else:
            description = title

        address = ''
        if 'rawData' in p and 'geographic' in p['rawData']:
            for each in p['rawData']['geographic']:
                if len(each.rstrip()) > len(address):
                    address = each.rstrip()

        licence = Licence.objects.get(pk=15)  # 15 = unknown licence
        if 'imageRights' in p and 'copyright' in p['imageRights']:
            licence_str = p['imageRights']['copyright']
            if licence_str:
                licence = Licence.objects.filter(name=licence_str).first()
                if not licence:
                    licence = Licence(
                        name=licence_str
                    )
                    licence.save()

        authors = []
        if 'authors' in p:
            if p['authors']['primary']:
                for k, each in p['authors']['primary'].items():
                    authors.append(k)

        source = Source.objects.filter(description=institution).first()
        if not source:
            source = Source(
                name=institution,
                description=institution
            )
            source.save()

        source = Source.objects.filter(description=institution).first()

        external_id = p['id'][:99]  # muis_id
        external_sub_id = None  # muis_media_id
        if '_' in p['id']:
            external_id = p['id'].split('_')[0]
            external_sub_id = p['id'].split('_')[1]

        new_photo = Photo(
            user=profile,
            author=comma.join(authors),
            title=finna_cut_title(p.get('title', None), p.get('title_short', None)),
            description=description,
            address=address[:255],
            source=source,
            types=None,
            keywords=None,
            date_text=p.get('year').encode('utf-8') if p.get('year', None) else None,
            licence=licence,
            external_id=external_id,
            external_sub_id=external_sub_id,
            source_key=p.get('id', None),
            source_url=f'https://www.finna.fi{p.get("recordPage")}',
            geography=geography
        )

        opener = build_opener()
        opener.addheaders = [('User-Agent', settings.UA)]
        img_url = get_img_url(p)
        img_response = opener.open(img_url)
        new_photo.image.save('finna.jpg', ContentFile(img_response.read()))

        new_photo.save()

        if p.get('latitude') and p.get('longitude') and not \
                GeoTag.objects.filter(type=GeoTag.SOURCE_GEOTAG, photo__source_key=new_photo.source_key).exists():
            source_geotag = GeoTag.objects.create(
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
            new_photo.latest_geotag = source_geotag.created
            new_photo.set_calculated_fields()

        new_photo.save()
        new_photo.add_to_source_album()

        return Photo.objects.filter(pk=new_photo.id).first()


def safe_list_get(my_list, idx, default):
    try:
        return my_list[idx]
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
            'field[]': ['id', 'title', 'shortTitle', 'images', 'imageRights', 'authors', 'source', 'geoLocations',
                        'recordPage',
                        'year', 'summary', 'rawData', 'imagesExtended'],
            'filter[]': [
                'free_online_boolean:"1"'
            ],

        }).text)

    def transform_response(self, response, remove_existing=False, finna_page=1):
        description2 = ''
        ids = None
        page_count = 0
        if 'records' in response:
            ids = [p['id'] for p in response['records']]
        if 'resultCount' in response:
            page_count = int(ceil(float(response['resultCount']) / float(self.page_size)))
        transformed = {
            'result': {
                'firstRecordViews': [],
                'page': finna_page,
                'pages': page_count
            }
        }
        if not ids:
            return dumps(transformed)
        existing_photos = Photo.objects.filter(source__description='Finna', external_id__in=ids).all()
        for p in response['records']:
            existing_photo = existing_photos.filter(external_id=p['id']).first()
            if remove_existing and existing_photo or 'images' not in p or not p['images']:
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
                            try:
                                p['longitude'] = float(lon)
                                p['latitude'] = float(lat)
                                break
                            except Exception as e:
                                print(e)
                                continue

                summary = ''
                if 'summary' in p:
                    for each in p['summary']:
                        if len(each.rstrip()) > len(summary):
                            summary = each.rstrip()

                address = ''
                if 'rawData' in p and 'geographic' in p['rawData']:
                    for each in p['rawData']['geographic']:
                        if len(each.rstrip()) > len(address):
                            address = each.rstrip()

                licence = None
                if 'imageRights' in p and 'copyright' in p['imageRights']:
                    licence = p['imageRights']['copyright']

                authors = []
                if 'authors' in p:
                    if p['authors']['primary']:
                        for k, each in p['authors']['primary'].items():
                            authors.append(k)

                # Cut long
                p['id'] = p['id'][:99]
                transformed_item = {
                    'isFinnaResult': True,
                    'id': p['id'],
                    'mediaId': p['id'],
                    'identifyingNumber': p['id'],
                    'title': finna_cut_title(p.get('title', None), p.get('shortTitle', None)),
                    'address': address,
                    'institution': institution,
                    'date': p.get('year', None),
                    'cachedThumbnailUrl': get_img_url(p, 'small'),
                    'imageUrl': get_img_url(p),
                    'urlToRecord': f'https://www.finna.fi{p.get("recordPage")}',
                    'latitude': p.get('latitude', None),
                    'longitude': p.get('longitude', None),
                    'creators': safe_list_get(authors, 0, None),
                    'licence': licence,
                    'description': description2 or p.get('summary', None),
                }
                if existing_photo:
                    transformed_item['ajapaikId'] = existing_photo.id
                    album_ids = AlbumPhoto.objects.filter(photo=existing_photo).values_list('album_id', flat=True)
                    transformed_item['albums'] = list(Album.objects.filter(pk__in=album_ids, atype=Album.CURATED)
                                                      .values_list('id', 'name').distinct())
                transformed['result']['firstRecordViews'].append(transformed_item)

        transformed = dumps(transformed)

        return transformed
