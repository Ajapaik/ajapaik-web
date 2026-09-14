import re
from html import unescape
from typing import List

import requests


def _get_licence_name_from_url(url):
    title = url
    try:
        html = requests.get(url, {}).text.replace('\n', '')
        title_search = re.search('<title>(.*)</title>', html, re.IGNORECASE)

        if title_search:
            title = title_search.group(1)
            title = unescape(title)
        return title
    except:  # noqa
        return title


def transform_fotis_persons_response(persons_str: str) -> List[str]:
    persons_str = persons_str.strip().strip(";")

    if ";" in persons_str:
        persons = persons_str.strip().split(";")
    else:
        persons = [persons_str]

    result = []
    for person in persons:
        person = person.strip()
        match = re.match(r'\b(\w+(?:\s*\w*))\s+\1\b', person)
        if match:
            result.append(match.groups()[0])
        elif person:
            result.append(person)

    return list(set(result))


def get_pending_curator_import_ids(source_description: str, ids: list) -> set:
    if not ids:
        return set()
    from ajapaik.ajapaik.models import CuratorImportItem
    str_ids = [str(x) for x in ids]
    return set(
        CuratorImportItem.objects.filter(
            source_description=source_description,
            external_id__in=str_ids,
            status__in=[CuratorImportItem.PENDING, CuratorImportItem.PROCESSING]
        ).values_list('external_id', flat=True)
    )
