from datetime import datetime
from datetime import timezone
import urllib

from django.core.management.base import BaseCommand

from ajapaik.ajapaik.muis_utils import add_dating_to_photo, add_person_albums, add_geotag_from_address_to_photo, \
    extract_dating_from_event, get_muis_date_and_prefix, set_text_fields_from_muis, reset_modeltranslated_field
from ajapaik.ajapaik.models import Album, AlbumPhoto, Dating, Photo, ApplicationException
import xml.etree.ElementTree as ET


class Command(BaseCommand):
    help = 'Update photos from MUIS'

    def handle(self, *args, **options):
        muis_url = 'https://www.muis.ee/OAIService/OAIService'
        all_person_album_ids_set = set()

        photos = Photo.objects.filter(source_url__contains='www.muis.ee/museaal')
        for photo in photos:
            try:
                parser = ET.XMLParser(encoding="utf-8")
                list_identifiers_url = muis_url + '?verb=GetRecord&identifier=' + photo.external_id \
                    + '&metadataPrefix=lido'
                url_response = urllib.request.urlopen(list_identifiers_url)
                tree = ET.fromstring(url_response.read(), parser=parser)
                ns = {'d': 'http://www.openarchives.org/OAI/2.0/', 'lido': 'http://www.lido-schema.org'}

                rec = tree.find('d:GetRecord/d:record', ns)
                record = 'd:metadata/lido:lidoWrap/lido:lido/'
                object_identification_wrap = record + 'lido:descriptiveMetadata/lido:objectIdentificationWrap/'
                object_description_wraps = \
                    object_identification_wrap + 'lido:objectDescriptionWrap/lido:objectDescriptionSet'
                title_wrap = object_identification_wrap + 'lido:titleWrap/'
                event_wrap = record + 'lido:descriptiveMetadata/lido:eventWrap/'
                actor_wrap = event_wrap + 'lido:eventSet/lido:event/lido:eventActor/'

                person_album_ids = []

                title_find = rec.find(title_wrap + 'lido:titleSet/lido:appellationValue', ns)
                title = title_find.text \
                    if title_find is not None \
                    else None
                photo = reset_modeltranslated_field(photo, title, 'title')
                photo.light_save()
                dating = None
                photo, dating = set_text_fields_from_muis(photo, dating, rec, object_description_wraps, ns)
                photo.light_save()
                creation_date_earliest = None
                creation_date_latest = None
                date_prefix_earliest = None
                date_prefix_latest = None
                date_earliest_has_suffix = False
                date_latest_has_suffix = False
                location = []
                events = rec.findall(event_wrap + 'lido:eventSet/lido:event', ns)
                existing_dating = Dating.objects.filter(photo=photo, profile=None).first()
                if events is not None and len(events) > 0:
                    location, \
                        creation_date_earliest, \
                        creation_date_latest, \
                        date_prefix_earliest, \
                        date_prefix_latest, \
                        date_earliest_has_suffix, \
                        date_latest_has_suffix, \
                        = extract_dating_from_event(
                            events,
                            location,
                            creation_date_earliest,
                            creation_date_latest,
                            dating is not None and existing_dating is None,
                            ns
                        )
                if dating is not None and existing_dating is None:
                    creation_date_earliest, date_prefix_earliest, date_earliest_has_suffix = \
                        get_muis_date_and_prefix(dating, False)
                    creation_date_latest, date_prefix_latest, date_latest_has_suffix = \
                        get_muis_date_and_prefix(dating, True)

                actors = rec.findall(actor_wrap + 'lido:actorInRole', ns)
                person_album_ids = add_person_albums(actors, person_album_ids, ns)
                if location != []:
                    photo = add_geotag_from_address_to_photo(photo, location)
                photo = add_dating_to_photo(
                    photo,
                    creation_date_earliest,
                    creation_date_latest,
                    date_prefix_earliest,
                    date_prefix_latest,
                    Dating,
                    date_earliest_has_suffix,
                    date_latest_has_suffix
                )
                dt = datetime.utcnow()
                dt.replace(tzinfo=timezone.utc)
                photo.muis_update_time = dt.replace(tzinfo=timezone.utc).isoformat()
                photo.light_save()

                person_albums = Album.objects.filter(id__in=person_album_ids)
                if person_albums is not None:
                    for album in person_albums:
                        if not album.cover_photo:
                            album.cover_photo = photo
                        ap = AlbumPhoto(photo=photo, album=album, type=AlbumPhoto.FACE_TAGGED)
                        ap.save()

                        all_person_album_ids_set.add(album.id)
            except Exception as e:
                exception = ApplicationException(exception=e, photo=photo)
                exception.save()
        all_person_album_ids = list(all_person_album_ids_set)
        all_person_albums = Album.objects.filter(id__in=all_person_album_ids)

        if all_person_albums is not None:
            for person_album in all_person_albums:
                person_album.set_calculated_fields()
                person_album.save()
