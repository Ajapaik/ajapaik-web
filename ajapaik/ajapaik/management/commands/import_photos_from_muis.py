import logging
import time
import traceback
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from urllib.parse import quote_plus

import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.timezone import now

from ajapaik.ajapaik.models import Album, AlbumPhoto, Photo, Source, ApplicationException
from ajapaik.ajapaik.muis_utils import add_person_albums, extract_dating_from_event, add_dating_to_photo, \
    add_geotag_from_address_to_photo, get_muis_date_and_prefix, set_text_fields_from_muis, reset_photo_translated_field
from ajapaik.ajapaik.utils import ImportBlacklistService


class Command(BaseCommand):
    help = 'Import photos from MUIS set'

    def add_arguments(self, parser):
        parser.add_argument(
            'set_name', nargs=1, type=str,
            help='Set name to import'
        )
        parser.add_argument(
            'album_ids', nargs='+', type=int,
            help='Album ids, where to import the photos from muis'
        )

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)

        # Import sets
        muis_url = 'https://www.muis.ee/OAIService/OAIService'
        set_name = (options['set_name'])[0]
        museum_name = set_name.split(':')[0]
        import_blacklist_service = ImportBlacklistService()
        ns = {'d': 'http://www.openarchives.org/OAI/2.0/', 'lido': 'http://www.lido-schema.org',
              'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}

        sets_url = f'{muis_url}?verb=ListSets'
        sets_response = requests.get(sets_url)

        if sets_response.status_code != 200:
            logger.info(f'Failed to get a response from MUIS API due to Server Error, {sets_url}')
            return

        if sets_response.text == '':
            logger.info(f'No results for MUIS API, {sets_url}')
            return

        tree = ET.fromstring(sets_response.text)
        sets = tree.findall('d:ListSets/d:set', ns)

        if not sets:
            logger.info(f'Did not find any sets to match with')
            return

        source = None
        set_exists = False
        for s in sets:
            if s.find('d:setSpec', ns).text == museum_name:
                logger.info(f"Found {museum_name}")
                museum_name = s.find('d:setName', ns).text
                source = Source.objects.filter(name=museum_name, description=museum_name).first()

                if not source:
                    Source.objects.create(name=museum_name, description=museum_name)

            if s.find('d:setSpec', ns).text == options['set_name'][0]:
                set_exists = True
                break

        if not set_exists:
            logger.info(f"Did not find set {options['set_name'][0]}")
            return

        dates = []
        start = datetime(2008, 3, 1)
        present = datetime.today() + timedelta(days=1)
        while present > start:
            dates.append(str(present.strftime('%Y-%m-%d')))
            present -= timedelta(days=30)
        dates.append(str(start.strftime('%Y-%m-%d')))

        until_date = None
        all_person_album_ids_set = set()
        album_ids = (options['album_ids'])
        albums = Album.objects.filter(id__in=album_ids)

        for from_date in dates:
            if until_date is None:
                until_date = from_date
                continue

            list_identifiers_url = f'{muis_url}?verb=ListRecords&set={quote_plus(set_name)}&from={from_date}' + \
                                   f'&until={until_date}&metadataPrefix=lido'
            until_date = from_date
            response = requests.get(list_identifiers_url)

            if response.status_code != 200:
                logger.info(f'Failed to get a response from MUIS API due to Server Error, {list_identifiers_url}')
                continue

            if response.text == '':
                logger.info(f'No results for MUIS API, {list_identifiers_url}')
                continue

            tree = ET.fromstring(response.text)
            header = 'd:header/'
            records = tree.findall('d:ListRecords/d:record', ns)
            record_wrap = 'd:metadata/lido:lidoWrap/lido:lido/'
            object_identification_wrap = f'{record_wrap}lido:descriptiveMetadata/lido:objectIdentificationWrap/'
            object_description_wraps = \
                f'{object_identification_wrap}lido:objectDescriptionWrap/lido:objectDescriptionSet'
            title_wrap = f'{object_identification_wrap}lido:titleWrap/'
            repository_wrap = f'{object_identification_wrap}lido:repositoryWrap/'
            event_wrap = f'{record_wrap}lido:descriptiveMetadata/lido:eventWrap/'
            resource_wrap = f'{record_wrap}lido:administrativeMetadata/lido:resourceWrap/'
            record_wrap_wrap = f'{record_wrap}lido:administrativeMetadata/lido:recordWrap/'
            actor_wrap = f'{event_wrap}lido:eventSet/lido:event/lido:eventActor/'

            for record in records:
                photo = None
                logger.info("Found record")
                try:
                    locations = []
                    person_album_ids = []
                    identifier_record = record.find(f'{header}d:identifier', ns)
                    # We can not check for identifier_record, as it will is falsy if it has no children
                    # That forces us to write these ugly is not None checks.
                    external_id = identifier_record.text if identifier_record is not None else None
                    existing_photo = Photo.objects.filter(external_id=external_id).first()

                    if existing_photo:
                        continue

                    rp_lr = 'lido:resourceRepresentation/lido:linkResource'
                    link_resource_record = record.find(f'{resource_wrap}lido:resourceSet/{rp_lr}', ns)
                    image_url = link_resource_record.text if link_resource_record is not None else None

                    if not image_url:
                        logger.info("No image url, skipping")
                        continue

                    file_extension = (link_resource_record.attrib['{' + ns['lido'] + '}formatResource']).lower()

                    if not image_url or file_extension not in ['gif', 'jpg', 'jpeg', 'png', 'tif', 'tiff', 'webp']:
                        logger.info(
                            "Skipping as there are no photos which are supported")
                        continue

                    source_url_find = record.find(f'{record_wrap_wrap}lido:recordInfoSet/lido:recordInfoLink', ns)
                    source_url = source_url_find.text \
                        if source_url_find is not None \
                        else None

                    if not source_url:
                        logger.warning(f'Found an record without an source URL! Skipping')
                        continue

                    identifier_find = record.find(f'{repository_wrap}lido:repositorySet/lido:workID', ns)
                    identifier = identifier_find.text if identifier_find is not None else None

                    if not identifier:
                        logger.warning(f'Found an record without an identifier! Skipping')
                        continue

                    if import_blacklist_service.is_blacklisted(identifier):
                        logger.info(f'Skipping {identifier} as it is blacklisted.')
                        continue

                    response = requests.get(image_url)

                    if response.status_code != 200:
                        logger.info(f"Skipping {identifier}, as we did not get a valid response when downloading.")
                        continue

                    logger.info("Sweet, let's add something")
                    img_data = response.content
                    image_id = external_id.split(':')[-1]
                    file_name = f'{set_name}_{image_id}.{file_extension}'
                    file_name = file_name.replace(':', '_')
                    path = f'{settings.MEDIA_ROOT}/uploads/{file_name}'

                    with open(path, 'wb') as handler:
                        handler.write(img_data)

                    photo = Photo(
                        image=path,
                        source_key=identifier,
                        source_url=source_url,
                        external_id=external_id,
                        source=source,
                        muis_update_time=now()
                    )
                    photo.light_save()
                    logger.info("Saving photo")

                    photo = Photo.objects.get(id=photo.id)
                    photo.image.name = f'uploads/{file_name}'

                    title_find = record.find(f'{title_wrap}lido:titleSet/lido:appellationValue', ns)
                    title = title_find.text \
                        if title_find is not None \
                        else None

                    if title:
                        photo = reset_photo_translated_field(photo, 'title', title)

                    photo, dating = set_text_fields_from_muis(photo, record, object_description_wraps, ns)
                    photo.light_save()
                    creation_date_earliest = None
                    creation_date_latest = None
                    date_prefix_earliest = None
                    date_prefix_latest = None
                    date_latest_has_suffix = False
                    events = record.findall(f'{event_wrap}lido:eventSet/lido:event', ns)

                    if events:
                        (locations,
                         creation_date_earliest,
                         creation_date_latest,
                         date_prefix_earliest,
                         date_prefix_latest,
                         date_latest_has_suffix) = extract_dating_from_event(
                            events,
                            locations,
                            creation_date_earliest,
                            creation_date_latest,
                            bool(dating),
                            ns
                        )

                    if dating:
                        creation_date_earliest, date_prefix_earliest, _ = \
                            get_muis_date_and_prefix(dating, False)
                        creation_date_latest, date_prefix_latest, date_latest_has_suffix = \
                            get_muis_date_and_prefix(dating, True)

                    actors = record.findall(f'{actor_wrap}lido:actorInRole', ns)
                    person_album_ids, author = add_person_albums(actors, person_album_ids, ns)

                    if author:
                        photo.author = author

                    person_albums = Album.objects.filter(id__in=person_album_ids)
                    if person_albums is not None:
                        for person_album in person_albums:
                            if not person_album.cover_photo:
                                person_album.cover_photo = photo
                            ap = AlbumPhoto(photo=photo, album=person_album, type=AlbumPhoto.FACE_TAGGED)
                            ap.save()
                            all_person_album_ids_set.add(person_album.id)

                    photo.add_to_source_album()

                    if locations and len(locations) > 0:
                        photo = add_geotag_from_address_to_photo(photo, locations)

                    photo = add_dating_to_photo(
                        photo,
                        creation_date_earliest,
                        creation_date_latest,
                        date_prefix_earliest,
                        date_prefix_latest,
                        date_latest_has_suffix,
                    )
                    photo.light_save()

                    for album in albums:
                        if not album.cover_photo:
                            album.cover_photo = photo
                        ap = AlbumPhoto(photo=photo, album=album, type=AlbumPhoto.CURATED)
                        ap.save()

                    photo.set_calculated_fields()
                except Exception as e:
                    logger.exception(e)
                    exception = ApplicationException(exception=traceback.format_exc(), photo=photo)
                    exception.save()

                time.sleep(1)

        for album in albums:
            album.light_save()

        all_person_album_ids = list(all_person_album_ids_set)
        all_person_albums = Album.objects.filter(id__in=all_person_album_ids)

        if all_person_albums:
            for person_album in all_person_albums:
                person_album.light_save()
