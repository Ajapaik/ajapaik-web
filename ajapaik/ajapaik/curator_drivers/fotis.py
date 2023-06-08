import math
from datetime import datetime, timedelta
from json import dumps, loads

from requests import get

from ajapaik.ajapaik.fotis_utils import transform_fotis_persons_response
from ajapaik.ajapaik.models import Photo, AlbumPhoto, Album


class FotisDriver(object):
    def __init__(self):
        self.search_url = 'https://www.ra.ee/fotis/api/index.php/v1/photo' \
                          '?filter[or][][reference_code][like]=%s' \
                          '&filter[or][][content][like]=%s' \
                          '&filter[or][][author][like]=%s' \
                          '&filter[or][][location][like]=%s' \
                          '&filter[or][][person][like]=%s' \
                          '&page=%s'

    def search(self, cleaned_data, max_results=200):
        fotis_multiplier = max_results / 20.0
        results = []
        response_headers = {}
        photo_external_ids = []

        while len(results) < max_results:
            previous_page = int(response_headers.get('X-Pagination-Current-Page', 0))

            if previous_page and previous_page >= int(response_headers.get('X-Pagination-Page-Count')):
                break

            new_page = previous_page + 1 if previous_page else cleaned_data['driverPage'] if cleaned_data[
                                                                                                 'driverPage'] < 2 else \
                (cleaned_data['driverPage'] * int(fotis_multiplier)) - (int(fotis_multiplier) - 1)
            response = get(self.search_url % (cleaned_data['fullSearch'], cleaned_data['fullSearch'],
                                              cleaned_data['fullSearch'], cleaned_data['fullSearch'],
                                              cleaned_data['fullSearch'],
                                              new_page), )
            response_headers = response.headers
            page_results = loads(response.text)

            filtered_results = []
            for result in page_results:
                result_id = result.get('id')
                if result_id and result_id not in photo_external_ids:
                    filtered_results.append(result)
                    photo_external_ids.append(result["id"])

            results += filtered_results

        # We've hacked FOTIS to make more queries instead of 1, thus we adjust page numbers accordingly
        return {
            'records': results[:max_results],
            'pageSize': 200,
            'page': math.ceil(int(response_headers['X-Pagination-Current-Page']) / fotis_multiplier),
            'pageCount': math.ceil(int(response_headers.get('X-Pagination-Page-Count')) / fotis_multiplier)
        }

    def transform_response(self, response, remove_existing=False, fotis_page=1):
        ids = [p['id'] for p in response['records']]
        transformed = {
            'result': {
                'firstRecordViews': [],
                'page': response['page'],
                'pages': response['pageCount']
            }
        }
        existing_photos = Photo.objects.filter(source__description='Fotis', external_id__in=ids).all()
        for p in response['records']:
            existing_photo = existing_photos.filter(external_id=p['id']).first()

            if remove_existing and existing_photo:
                continue
            else:
                persons_str = p.get('person')  # Fotis API doesn't have a nice name for persons
                dating = p.get('dating', {})

                start_ts = dating.get('date_beginning_timestamp')
                end_ts = dating.get('date_end_timestamp')

                start_date = datetime(1970, 1, 1) + timedelta(seconds=float(start_ts)) if start_ts else None
                end_date = datetime(1970, 1, 1) + timedelta(seconds=float(end_ts)) if end_ts else None

                title = p.get('content') or p['content_original']
                transformed_item = {
                    'id': p['id'],
                    'isFotisResult': True,
                    'identifyingNumber': p['reference_code'],
                    'title': title,
                    'institution': 'Fotis',
                    'cachedThumbnailUrl': p['_links']['image']['href'],
                    # HACK: new image url for image files without the black strip below
                    'imageUrl': f'https://www.meediateek.ee/photo/full?id={p["id"]}',
                    'urlToRecord': p['_links']['view']['href'],
                    'creators': p['author'],
                    'persons': transform_fotis_persons_response(persons_str) if persons_str else [],
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None,
                    'date_start_accuracy': dating.get('date_beginning_accuracy'),
                    'date_end_accuracy': dating.get('date_end_accuracy')  # Kuupäev, Kuu, Aasta, Kümnend, Sajand
                }

                if existing_photo:
                    transformed_item['ajapaikId'] = existing_photo.id
                    album_ids = AlbumPhoto.objects.filter(photo=existing_photo).values_list('album_id', flat=True)
                    transformed_item['albums'] = list(Album.objects.filter(pk__in=album_ids, atype=Album.CURATED)
                                                      .values_list('id', 'name').distinct())
                transformed['result']['firstRecordViews'].append(transformed_item)
        transformed = dumps(transformed)

        return transformed
