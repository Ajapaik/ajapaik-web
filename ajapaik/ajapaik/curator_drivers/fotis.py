from json import dumps, loads

from requests import get

from ajapaik.ajapaik.curator_drivers.curator_utils import handle_existing_photos
from ajapaik.ajapaik.models import Photo


def safe_list_get(my_list, idx, default):
    try:
        return my_list[idx]
    except IndexError:
        return default


class FotisDriver(object):
    def __init__(self):
        self.search_url = 'https://www.ra.ee/fotis/api/index.php/v1/photo' \
                          '?filter[or][][reference_code][like]=%s' \
                          '&filter[or][][content][like]=%s' \
                          '&filter[or][][author][like]=%s' \
                          '&filter[or][][location][like]=%s' \
                          '&page=%s'

    def search(self, cleaned_data):
        response = get(self.search_url % (cleaned_data['fullSearch'], cleaned_data['fullSearch'],
                                          cleaned_data['fullSearch'], cleaned_data['fullSearch'],
                                          cleaned_data['flickrPage']), )
        response_headers = response.headers
        results = loads(response.text)

        return {
            'records': results,
            'pageSize': response_headers['X-Pagination-Per-Page'],
            'page': response_headers['X-Pagination-Current-Page'],
            'pageCount': response_headers['X-Pagination-Page-Count']
        }

    def transform_response(self, response, remove_existing=False, fotis_page=1):
        ids = [p['id'] for p in response['records']]
        transformed = {
            'result': {
                'firstRecordViews': [],
                'page': fotis_page,
                'pages': response['pageCount']
            }
        }
        existing_photos = Photo.objects.filter(source__description='Fotis', external_id__in=ids).all()
        for p in response['records']:
            existing_photo = existing_photos.filter(external_id=p['id']).first()
            if remove_existing and existing_photo:
                continue
            else:
                # TODO: Handle weird dating format
                # FIXME: Fotis SSL is broken, don't use https URLs until they figure it out
                # image_url = p['_links']['image']['href'].replace('http://', 'https://')
                transformed_item = {
                    'isFotisResult': True,
                    'id': p['id'],
                    'identifyingNumber': p['reference_code'],
                    'title': p['content'] if p['content'] else p['content_original'],
                    'institution': 'Fotis',
                    'cachedThumbnailUrl': p['_links']['image']['href'],
                    'imageUrl': p['_links']['image']['href'],
                    # 'urlToRecord': p['_links']['view']['href'].replace('http://', 'https://'),
                    'urlToRecord': p['_links']['view']['href'],
                    'creators': p['author']
                }

                transformed['result']['firstRecordViews'].append(
                    handle_existing_photos(existing_photo, transformed_item))
        transformed = dumps(transformed)

        return transformed
