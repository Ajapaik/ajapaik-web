from datetime import datetime, timedelta
from json import dumps, loads

from django.conf import settings
from requests import get

from ajapaik.ajapaik.models import Photo, AlbumPhoto, Album
from ajapaik.ajapaik_curator.utils import transform_fotis_persons_response, get_pending_curator_import_ids


class FotisDriver(object):
    def __init__(self):
        # Base URLs for broad search and specific reference code search
        self.broad_search_url = 'https://www.ra.ee/fotis/api/index.php/v1/photo' \
                                '?filter[or][][reference_code][like]=%s' \
                                '&filter[or][][content][like]=%s' \
                                '&filter[or][][author][like]=%s' \
                                '&filter[or][][location][like]=%s' \
                                '&filter[or][][person][like]=%s' \
                                '&per-page=100' \
                                '&page=%s'
        self.ref_search_url = 'https://www.ra.ee/fotis/api/index.php/v1/photo' \
                              '?filter[reference_code][like]=%s' \
                              '&per-page=100' \
                              '&page=%s'

    def search(self, cleaned_data, max_results=20):
        # We process one page at a time to avoid server-side timeouts
        # The frontend will now handle multi-page fetching
        query = cleaned_data['fullSearch']
        page = cleaned_data.get('driverPage', 1)

        if cleaned_data.get('referenceCodeOnly'):
            url = self.ref_search_url % (query, page)
        else:
            url = self.broad_search_url % (query, query, query, query, query, page)

        headers = {'User-Agent': settings.UA}
        response = get(url, headers=headers, timeout=15)
        response_headers = response.headers
        if response.status_code == 200:
            results = loads(response.text)
        else:
            results = []

        # Ensure we always return a dictionary consistent with expected structure
        return {
            'records': results,
            'pageSize': 100,
            'page': int(response_headers.get('X-Pagination-Current-Page', page)),
            'pageCount': int(response_headers.get('X-Pagination-Page-Count', 1))
        }

    def _transform_single_record(self, p, existing_photo, is_pending):
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
            'imageUrl': p['_links']['image']['href'],
            'urlToRecord': f'https://www.meediateek.ee/photo/view?id={p["id"]}',
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
        elif is_pending:
            transformed_item['isPending'] = True

        return transformed_item

    def transform_response(self, response, remove_existing=False):
        ids = [p['id'] for p in response['records']]
        existing_photos = {
            str(p.external_id): p
            for p in Photo.objects.filter(source__description='Fotis', external_id__in=ids)
        }
        pending_ids = get_pending_curator_import_ids('Fotis', ids)
        first_record_views = []

        for p in response['records']:
            pid_str = str(p['id'])
            existing_photo = existing_photos.get(pid_str)
            is_pending = pid_str in pending_ids

            if remove_existing and (existing_photo or is_pending):
                continue

            first_record_views.append(self._transform_single_record(p, existing_photo, is_pending))

        return dumps({
            'result': {
                'firstRecordViews': first_record_views,
                'page': response['page'],
                'pages': response['pageCount']
            }
        })
