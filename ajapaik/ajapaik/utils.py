import json
import re
import sys
from math import ceil

from django.conf import settings

from ajapaik.ajapaik.models import ImportBlacklist, Photo
from ajapaik.ajapaik_curator.curator_drivers.finna import finna_import_photo, finna_add_to_album


def get_pagination_parameters(page, total, page_size=settings.FRONTPAGE_DEFAULT_ALBUM_PAGE_SIZE):
    start = (page - 1) * page_size
    max_page = ceil(float(total) / float(page_size))
    if page > max_page:
        page = max_page

    if start < 0:
        start = 0
    if start > total:
        start = total
    if int(start + page_size) > total:
        end = total
    else:
        end = start + page_size
    end = int(end)

    return start, end, max_page, page


class ImportBlacklistService:
    def __init__(self):
        self.blacklisted_keys = list(
            ImportBlacklist.objects.exclude(source_key=None).values_list('source_key', flat=True))
        self.blacklisted_key_patterns = list(ImportBlacklist.objects.exclude(source_key_pattern=None).values_list(
            'source_key_pattern', flat=True))

    def is_blacklisted(self, source_key: str) -> bool:
        if source_key in self.blacklisted_keys:
            return True

        if any(re.compile(pattern).match(source_key) for pattern in self.blacklisted_key_patterns):
            return True

        return False


def find_finna_photo_by_url(record_url, profile):
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


def _join_2_json_objects(obj1, obj2):
    result = {'firstRecordViews': []}
    # TODO: Why do errors sometimes happen here?
    try:
        result = extract_values_from_dictionary_to_result(json.loads(obj1), result)
        result = extract_values_from_dictionary_to_result(json.loads(obj2), result)
    except TypeError:
        print('Could not extract values from dictionary', file=sys.stderr)

    return json.dumps({'result': result})


def extract_values_from_dictionary_to_result(dictionary: dict, result: dict):
    try:
        if 'result' in dictionary:
            for each in dictionary['result']['firstRecordViews']:
                result['firstRecordViews'].append(each)
            if 'page' in dictionary['result']:
                result['page'] = dictionary['result']['page']
            if 'pages' in dictionary['result']:
                result['pages'] = dictionary['result']['pages']
            if 'ids' in dictionary['result']:
                result['ids'] = dictionary['result']['ids']
    except TypeError:
        print('Could not extract values from dictionary', file=sys.stderr)

    return result


def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'
