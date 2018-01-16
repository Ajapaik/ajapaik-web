from json import dumps, loads
from math import ceil

from requests import get

from project.ajapaik.models import Photo, AlbumPhoto, Album


def safe_list_get(l, idx, default):
    try:
        return l[idx]
    except IndexError:
        return default


class FotisDriver(object):
    def __init__(self):
        self.search_url = 'http://www.ra.ee/apps/fotis/api/index.php/v1/photo' \
                          '?filter[or][][reference_code][like]=%s' \
                          '&filter[or][][content][like]=%s' \
                          '&filter[or][][author][like]=%s' \
                          '&filter[or][][location][like]=%s'
        self.page_size = 20

    def search(self, cleaned_data):
        return loads(
            get(self.search_url % (cleaned_data['fullSearch'], cleaned_data['fullSearch'], cleaned_data['fullSearch'],
                                   cleaned_data['fullSearch']), {}).text)

    def transform_response(self, response, remove_existing=False, finna_page=1):
        # TODO: Rewrite for Fotis
        return []
        # ids = [p['id'] for p in response['records']]
        # page_count = int(ceil(float(response['resultCount']) / float(self.page_size)))
        # transformed = {
        #     'result': {
        #         'firstRecordViews': [],
        #         'page': finna_page,
        #         'pages': page_count
        #     }
        # }
        # existing_photos = Photo.objects.filter(source__description='Finna', external_id__in=ids).all()
        # for p in response['records']:
        #     existing_photo = existing_photos.filter(external_id=p['id']).first()
        #     if remove_existing and existing_photo or 'images' not in p:
        #         continue
        #     else:
        #         institution = 'Finna'
        #         if p['source']:
        #             if 'translated' in p['source'][0]:
        #                 institution = p['source'][0]['translated']
        #             elif 'value' in p['source'][0]:
        #                 institution = p['source'][0]['value']
        #         if 'geoLocations' in p:
        #             for each in p['geoLocations']:
        #                 if 'POINT' in each:
        #                     point_parts = each.split(' ')
        #                     lon = point_parts[0][6:]
        #                     lat = point_parts[1][:-1]
        #                     p['longitude'] = lon
        #                     p['latitude'] = lat
        #         licence = None
        #         if 'imageRights' in p and 'copyright' in p['imageRights']:
        #             licence = p['imageRights']['copyright']
        #         transformed_item = {
        #             'isFinnaResult': True,
        #             'id': p['id'],
        #             'mediaId': p['id'],
        #             'identifyingNumber': p['id'],
        #             'title': p['title'],
        #             'institution': institution,
        #             'date': p.get('year', None),
        #             'cachedThumbnailUrl': 'https://www.finna.fi' + p['images'][0],
        #             'imageUrl': 'https://www.finna.fi' + p['images'][0],
        #             'urlToRecord': 'https://www.finna.fi' + p['recordPage'],
        #             'latitude': p.get('latitude', None),
        #             'longitude': p.get('longitude', None),
        #             'creators': safe_list_get(p.get('authors', {}).get('main', {}).items(), 0, None),
        #             'licence': licence
        #         }
        #         if existing_photo:
        #             transformed_item['ajapaikId'] = existing_photo.id
        #             album_ids = AlbumPhoto.objects.filter(photo=existing_photo).values_list('album_id', flat=True)
        #             transformed_item['albums'] = Album.objects.filter(pk__in=album_ids, atype=Album.CURATED) \
        #                 .values_list('id', 'name')
        #         transformed['result']['firstRecordViews'].append(transformed_item)
        #
        # transformed = dumps(transformed)
        #
        # return transformed
