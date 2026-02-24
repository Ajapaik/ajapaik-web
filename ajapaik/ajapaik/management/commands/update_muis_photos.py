import logging
import xml.etree.ElementTree as ET

import requests
from django.core.management.base import BaseCommand
from django.utils.timezone import now

from ajapaik.ajapaik.models import Album, AlbumPhoto, Photo, ApplicationException
from ajapaik.ajapaik.muis_utils import add_dating_to_photo, add_person_albums, add_geotag_from_address_to_photo, \
    extract_dating_from_event, get_muis_date_and_prefix, set_text_fields_from_muis, reset_photo_translated_field


class Command(BaseCommand):
    help = 'Update photos from MUIS'

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)

        muis_url = 'https://www.muis.ee/OAIService/OAIService'
        all_person_album_ids_set = set()

        photos = Photo.objects.filter(source_url__contains='muis.ee')
        for photo in photos:
            try:
                list_identifiers_url = f'{muis_url}?verb=GetRecord&identifier={photo.external_id}&metadataPrefix=lido'
                response = requests.get(list_identifiers_url)

                if response.status_code != 200:
                    logger.info(f'Failed to get a response from MUIS API due to Server Error, {list_identifiers_url}')
                    continue

                if response.text == '':
                    logger.info(f'No results for MUIS API, {list_identifiers_url}')
                    continue

                tree = ET.fromstring(response.read())
                ns = {'d': 'http://www.openarchives.org/OAI/2.0/', 'lido': 'http://www.lido-schema.org'}

                rec = tree.find('d:GetRecord/d:record', ns)
                record = 'd:metadata/lido:lidoWrap/lido:lido/'
                object_identification_wrap = f'{record}lido:descriptiveMetadata/lido:objectIdentificationWrap/'
                object_description_wraps = \
                    f'{object_identification_wrap}lido:objectDescriptionWrap/lido:objectDescriptionSet'
                title_wrap = f'{object_identification_wrap}lido:titleWrap/'
                event_wrap = f'{record}lido:descriptiveMetadata/lido:eventWrap/'
                actor_wrap = f'{event_wrap}lido:eventSet/lido:event/lido:eventActor/'

                person_album_ids = []

                title_find = rec.find(f'{title_wrap}lido:titleSet/lido:appellationValue', ns)
                title = title_find.text \
                    if title_find is not None \
                    else None
                photo = reset_photo_translated_field(photo, 'title', title)

                photo, dating = set_text_fields_from_muis(photo, rec, object_description_wraps, ns)
                creation_date_earliest = None
                creation_date_latest = None
                date_prefix_earliest = None
                date_prefix_latest = None
                date_latest_has_suffix = False
                location = []
                events = rec.findall(f'{event_wrap}lido:eventSet/lido:event', ns)
                existing_dating = photo.datings.filter(profile=None).first()
                has_new_dating_data = dating is not None and not existing_dating

                if events:
                    location, \
                    creation_date_earliest, \
                    creation_date_latest, \
                    date_prefix_earliest, \
                    date_prefix_latest, \
                    date_latest_has_suffix, \
                        = extract_dating_from_event(
                        events,
                        location,
                        creation_date_earliest,
                        creation_date_latest,
                        has_new_dating_data,
                        ns
                    )
                if dating is not None and existing_dating is None:
                    creation_date_earliest, date_prefix_earliest, date_earliest_has_suffix = \
                        get_muis_date_and_prefix(dating, False)
                    creation_date_latest, date_prefix_latest, date_latest_has_suffix = \
                        get_muis_date_and_prefix(dating, True)

                actors = rec.findall(f'{actor_wrap}lido:actorInRole', ns)
                person_album_ids, author = add_person_albums(actors, person_album_ids, ns)

                if author is not None:
                    photo.author = author

                if location:
                    photo = add_geotag_from_address_to_photo(photo, location)

                person_albums = Album.objects.filter(id__in=person_album_ids) or []
                for album in person_albums:
                    if not album.cover_photo:
                        album.cover_photo = photo
                    ap = AlbumPhoto(photo=photo, album=album, type=AlbumPhoto.FACE_TAGGED)
                    ap.save()
                    all_person_album_ids_set.add(album.id)

                photo.set_calculated_fields()

                photo = add_dating_to_photo(
                    photo,
                    creation_date_earliest,
                    creation_date_latest,
                    date_prefix_earliest,
                    date_prefix_latest,
                    date_latest_has_suffix
                )
                photo.muis_update_time = now()
                photo.light_save()

            except Exception as e:
                logger.info(e)
                exception = ApplicationException(exception=e, photo=photo)
                exception.save()

        all_person_album_ids = list(all_person_album_ids_set)
        all_person_albums = Album.objects.filter(id__in=all_person_album_ids)

        if all_person_albums is not None:
            for person_album in all_person_albums:
                person_album.set_calculated_fields()
                person_album.save()
