from datetime import datetime, timedelta
from json import dumps, loads

from django.conf import settings
from requests import get

from ajapaik.ajapaik.models import Album, AlbumPhoto, Photo
from ajapaik.ajapaik_curator.utils import transform_fotis_persons_response


class FotisDriver:
    def __init__(self):
        # Base URLs for broad search and specific reference code search (API v2)
        self.broad_search_url = (
            "https://www.ra.ee/fotis/api/index.php/v2/photo"
            "?filter[or][][reference_code][like]=%s"
            "&filter[or][][content][like]=%s"
            "&filter[or][][author][like]=%s"
            "&filter[or][][location][like]=%s"
            "&filter[or][][person][like]=%s"
            "&per-page=100"
            "&page=%s"
        )
        self.ref_search_url = (
            "https://www.ra.ee/fotis/api/index.php/v2/photo"
            "?filter[reference_code][like]=%s"
            "&per-page=100"
            "&page=%s"
        )

    def search(self, cleaned_data, max_results=20):
        # We process one page at a time to avoid server-side timeouts
        # The frontend will now handle multi-page fetching
        query = cleaned_data["fullSearch"]
        page = cleaned_data.get("driverPage", 1)

        if cleaned_data.get("referenceCodeOnly"):
            url = self.ref_search_url % (query, page)
        else:
            url = self.broad_search_url % (query, query, query, query, query, page)

        headers = {"User-Agent": settings.UA}
        response = get(url, headers=headers, timeout=15)
        response_headers = response.headers
        if response.status_code == 200:
            results = loads(response.text)
        else:
            results = []

        # Ensure we always return a dictionary consistent with expected structure
        return {
            "records": results,
            "pageSize": 100,
            "page": int(response_headers.get("X-Pagination-Current-Page", page)),
            "pageCount": int(response_headers.get("X-Pagination-Page-Count", 1)),
        }

    def transform_response(self, response, remove_existing=False):
        ids = [p["id"] for p in response["records"]]
        transformed = {
            "result": {
                "firstRecordViews": [],
                "page": response["page"],
                "pages": response["pageCount"],
            }
        }
        existing_photos = Photo.objects.filter(
            source__description="Fotis", external_id__in=ids
        ).all()
        for p in response["records"]:
            existing_photo = existing_photos.filter(external_id=p["id"]).first()

            if remove_existing and existing_photo:
                continue
            else:
                raw_persons = p.get("person")
                clean_names = []
                fotis_persons = []
                if isinstance(raw_persons, list):
                    for per in raw_persons:
                        fname = (per.get("name") or "").strip()
                        sname = (per.get("surname") or "").strip()
                        fullname = f"{fname} {sname}".strip()
                        if fullname and fullname not in clean_names:
                            clean_names.append(fullname)
                        fotis_persons.append(per)
                elif isinstance(raw_persons, str) and raw_persons.strip():
                    clean_names = transform_fotis_persons_response(raw_persons)
                    fotis_persons = []

                dating = p.get("dating", {})

                start_ts = dating.get("date_beginning_timestamp")
                end_ts = dating.get("date_end_timestamp")

                start_date = (
                    datetime(1970, 1, 1) + timedelta(seconds=float(start_ts))
                    if start_ts
                    else None
                )
                end_date = (
                    datetime(1970, 1, 1) + timedelta(seconds=float(end_ts))
                    if end_ts
                    else None
                )

                title = p.get("content") or p["content_original"]
                transformed_item = {
                    "id": p["id"],
                    "isFotisResult": True,
                    "identifyingNumber": p["reference_code"],
                    "title": title,
                    "institution": "Fotis",
                    "cachedThumbnailUrl": p["_links"]["image"]["href"],
                    "imageUrl": p["_links"]["image"]["href"],
                    "urlToRecord": f"https://www.meediateek.ee/photo/view?id={p['id']}",
                    "creators": p["author"],
                    "persons": clean_names,
                    "fotis_persons": fotis_persons,
                    "faces": p.get("faces", []),
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None,
                    "date_start_accuracy": dating.get("date_beginning_accuracy"),
                    "date_end_accuracy": dating.get(
                        "date_end_accuracy"
                    ),  # Kuupäev, Kuu, Aasta, Kümnend, Sajand
                }

                if existing_photo:
                    transformed_item["ajapaikId"] = existing_photo.id
                    album_ids = AlbumPhoto.objects.filter(
                        photo=existing_photo
                    ).values_list("album_id", flat=True)
                    transformed_item["albums"] = list(
                        Album.objects.filter(pk__in=album_ids, atype=Album.CURATED)
                        .values_list("id", "name")
                        .distinct()
                    )
                transformed["result"]["firstRecordViews"].append(transformed_item)
        transformed = dumps(transformed)

        return transformed
