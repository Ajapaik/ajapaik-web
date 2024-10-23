import logging
import time
import traceback
import urllib
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from urllib.parse import quote

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Album, AlbumPhoto, Dating, Photo, Source, ApplicationException
from ajapaik.ajapaik.muis_utils import add_person_albums, extract_dating_from_event, add_dating_to_photo, \
    add_geotag_from_address_to_photo, get_muis_date_and_prefix, set_text_fields_from_muis, reset_modeltranslated_field
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
        source = Source.objects.filter(name=museum_name).first()
        import_blacklist_service = ImportBlacklistService()

        if source is None:
            sets_url = f'{muis_url}?verb=ListSets'
            url_response = urllib.request.urlopen(sets_url)
            parser = ET.XMLParser(encoding="utf-8")
            tree = ET.fromstring(url_response.read(), parser=parser)
            ns = {'d': 'http://www.openarchives.org/OAI/2.0/'}
            sets = tree.findall('d:ListSets/d:set', ns)
            for s in sets:
                if s.find('d:setSpec', ns).text == museum_name:
                    source_description = s.find('d:setName', ns).text
                    Source.objects.create(name=museum_name, description=source_description)
                    break

        source = Source.objects.filter(name=museum_name).first()

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

            list_identifiers_url = f'{muis_url}?verb=ListRecords&set={quote(set_name)}&from={from_date}' + \
                                   f'&until={until_date}&metadataPrefix=lido'
            url_response = urllib.request.urlopen(list_identifiers_url)
            parser = ET.XMLParser(encoding="utf-8")
            redurl = url_response.read()
            tree = ET.fromstring(redurl, parser=parser)
            ns = {'d': 'http://www.openarchives.org/OAI/2.0/', 'lido': 'http://www.lido-schema.org'}
            header = 'd:header/'
            records = tree.findall('d:ListRecords/d:record', ns)
            record = 'd:metadata/lido:lidoWrap/lido:lido/'
            object_identification_wrap = f'{record}lido:descriptiveMetadata/lido:objectIdentificationWrap/'
            object_description_wraps = \
                f'{object_identification_wrap}lido:objectDescriptionWrap/lido:objectDescriptionSet'
            title_wrap = f'{object_identification_wrap}lido:titleWrap/'
            repository_wrap = f'{object_identification_wrap}lido:repositoryWrap/'
            event_wrap = f'{record}lido:descriptiveMetadata/lido:eventWrap/'
            record_wrap = f'{record}lido:administrativeMetadata/lido:recordWrap/'
            resource_wrap = f'{record}lido:administrativeMetadata/lido:resourceWrap/'
            actor_wrap = f'{event_wrap}lido:eventSet/lido:event/lido:eventActor/'

            for rec in records:
                try:
                    locations = []
                    person_album_ids = []
                    identifier_record = rec.find(f'{header}d:identifier', ns)
                    external_id = identifier_record.text if identifier_record else None
                    existing_photo = Photo.objects.filter(external_id=external_id).first()

                    if existing_photo:
                        continue

                    rp_lr = 'resourceRepresentation/lido:linkResource'
                    link_resource_record = rec.find(f'{resource_wrap}lido:resourceSet/lido:{rp_lr}', ns)
                    image_url = link_resource_record.text if link_resource_record else None

                    if link_resource_record:
                        image_extension = (link_resource_record.attrib['{' + ns['lido'] + '}formatResource']).lower()
                    else:
                        image_extension = None

                    source_url_find = rec.find(f'{record_wrap}lido:recordInfoSet/lido:recordInfoLink', ns)
                    source_url = source_url_find.text \
                        if source_url_find is not None \
                        else None

                    identifier_find = rec.find(f'{repository_wrap}lido:repositorySet/lido:workID', ns)
                    identifier = identifier_find.text if identifier_find else None

                    if identifier and import_blacklist_service.is_blacklisted(identifier):
                        logger.info(f'Skipping {identifier} as it is blacklisted.')
                        continue

                    if not image_url or image_extension not in ['gif', 'jpg', 'jpeg', 'png', 'tif', 'tiff', 'webp']:
                        logger.info(f"Skipping {identifier}, as there are no photos which are supported")
                        continue

                    response = requests.get(image_url)

                    if response.status_code != 200:
                        logger.info(f"Skipping {identifier}, as we did not get a valid response when downloading")

                    img_data = response.content
                    image_id = external_id.split(':')[-1]
                    file_name = f'{set_name}_{image_id}.{image_extension}'
                    file_name = file_name.replace(':', '_')
                    path = f'{settings.MEDIA_ROOT}/uploads/{file_name}'
                    with open(path, 'wb') as handler:
                        handler.write(img_data)
                    photo = Photo(
                        image=path,
                        source_key=identifier,
                        source_url=source_url,
                        external_id=external_id,
                        source=source
                    )
                    dt = datetime.utcnow()
                    photo.muis_update_time = dt.replace(tzinfo=timezone.utc).isoformat()
                    photo.light_save()

                    photo = Photo.objects.get(id=photo.id)
                    photo.image.name = f'uploads/{file_name}'

                    title_find = rec.find(f'{title_wrap}lido:titleSet/lido:appellationValue', ns)
                    title = title_find.text \
                        if title_find is not None \
                        else None

                    if title:
                        photo = reset_modeltranslated_field(photo, 'title', title)

                    dating = None
                    photo, dating = set_text_fields_from_muis(photo, dating, rec, object_description_wraps, ns)
                    photo.light_save()
                    creation_date_earliest = None
                    creation_date_latest = None
                    date_prefix_earliest = None
                    date_prefix_latest = None
                    date_earliest_has_suffix = False
                    date_latest_has_suffix = False
                    events = rec.findall(f'{event_wrap}lido:eventSet/lido:event', ns)
                    if events and len(events) > 0:
                        (locations,
                         creation_date_earliest,
                         creation_date_latest,
                         date_prefix_earliest,
                         date_prefix_latest,
                         date_earliest_has_suffix,
                         date_latest_has_suffix) = extract_dating_from_event(
                            events,
                            locations,
                            creation_date_earliest,
                            creation_date_latest,
                            photo.latest_dating is not None or dating is not None,
                            ns
                        )
                    if dating:
                        creation_date_earliest, date_prefix_earliest, date_earliest_has_suffix = \
                            get_muis_date_and_prefix(dating, False)
                        creation_date_latest, date_prefix_latest, date_latest_has_suffix = \
                            get_muis_date_and_prefix(dating, True)

                    actors = rec.findall(f'{actor_wrap}lido:actorInRole', ns)
                    person_album_ids, author = add_person_albums(actors, person_album_ids, ns)
                    if author:
                        photo.author = author

                    photo.add_to_source_album()
                    if locations and len(locations) > 0:
                        photo = add_geotag_from_address_to_photo(photo, locations)

                    photo = add_dating_to_photo(
                        photo,
                        creation_date_earliest,
                        creation_date_latest,
                        date_prefix_earliest,
                        date_prefix_latest,
                        Dating,
                        date_earliest_has_suffix,
                        date_latest_has_suffix,
                    )
                    photo.light_save()

                    for album in albums:
                        if not album.cover_photo:
                            album.cover_photo = photo
                        ap = AlbumPhoto(photo=photo, album=album, type=AlbumPhoto.CURATED)
                        ap.save()

                    person_albums = Album.objects.filter(id__in=person_album_ids)
                    if person_albums is not None:
                        for person_album in person_albums:
                            if not person_album.cover_photo:
                                person_album.cover_photo = photo
                            ap = AlbumPhoto(photo=photo, album=person_album, type=AlbumPhoto.FACE_TAGGED)
                            ap.save()
                            all_person_album_ids_set.add(person_album.id)

                    photo.set_calculated_fields()
                except Exception as e:
                    logger.exception(e)
                    exception = ApplicationException(exception=traceback.format_exc(), photo=photo)
                    exception.save()

                time.sleep(1)
            until_date = from_date

        for album in albums:
            album.light_save()

        all_person_album_ids = list(all_person_album_ids_set)
        all_person_albums = Album.objects.filter(id__in=all_person_album_ids)

        if all_person_albums:
            for person_album in all_person_albums:
                person_album.light_save()
