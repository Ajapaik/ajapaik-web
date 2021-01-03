import urllib

from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Album, AlbumPhoto, Dating, GeoTag, Photo, Source
import xml.etree.ElementTree as ET
import requests
from django.conf import settings
import json


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
        creation_event_types = ['valmistamine', '<valmistamine/tekkimine>', 'pildistamine']
        set_name = (options['set_name'])[0]
        album_ids = (options['album_ids'])
        albums = Album.objects.filter(id__in=album_ids)
        all_person_album_ids_set = set()

        museum_name = set_name.split(':')[0]
        source = Source.objects.filter(name=museum_name).first()

        muis_url = 'https://www.muis.ee/OAIService/OAIService'
        if source is None:
            sets_url = muis_url + '?verb=ListSets'
            url_response = urllib.request.urlopen(sets_url)
            parser = ET.XMLParser(encoding="utf-8")
            tree = ET.fromstring(url_response.read(), parser=parser)
            ns = {'d': 'http://www.openarchives.org/OAI/2.0/'}
            sets = tree.findall('d:ListSets/d:set', ns)
            for s in sets:
                if s.find('d:setSpec', ns).text == museum_name:
                    source_description = s.find('d:setName', ns).text
            source = Source(name=museum_name, description=source_description)
            source.save()
        source = Source.objects.filter(name=museum_name).first()

        list_identifiers_url = muis_url + '?verb=ListRecords&set=' + set_name \
            + '&metadataPrefix=lido'
        url_response = urllib.request.urlopen(list_identifiers_url)
        parser = ET.XMLParser(encoding="utf-8")
        tree = ET.fromstring(url_response.read(), parser=parser)
        ns = {'d': 'http://www.openarchives.org/OAI/2.0/', 'lido': 'http://www.lido-schema.org'}

        header = 'd:header/'
        records = tree.findall('d:ListRecords/d:record', ns)
        record = 'd:metadata/lido:lidoWrap/lido:lido/'
        object_identification_wrap = record + 'lido:descriptiveMetadata/lido:objectIdentificationWrap/'
        description_wrap = object_identification_wrap + 'lido:titleWrap/'
        repository_wrap = object_identification_wrap + 'lido:repositoryWrap/'
        event_wrap = record + 'lido:descriptiveMetadata/lido:eventWrap/'
        record_wrap = record + 'lido:administrativeMetadata/lido:recordWrap/'
        resource_wrap = record + 'lido:administrativeMetadata/lido:resourceWrap/'
        actor_wrap = event_wrap + 'lido:eventSet/lido:event/lido:eventActor/'

        for rec in records:
            person_album_ids = []

            external_id = rec.find(header + 'd:identifier', ns).text \
                if rec.find(header + 'd:identifier', ns) is not None \
                else None

            existing_photo = Photo.objects.filter(source=source, external_id=external_id).first()
            if existing_photo is not None:
                continue

            description_find = rec.find(description_wrap + 'lido:titleSet/lido:appellationValue', ns)
            description = description_find.text \
                if description_find is not None \
                else None

            creation_date_earliest = None
            creation_date_latest = None
            location = ''
            events = rec.findall(event_wrap + 'lido:eventSet/lido:event', ns)
            if events is not None:
                for event in events:
                    if location != '':
                        break
                    event_types = event.findall('lido:eventType/lido:term', ns)
                    if event_types is None:
                        continue
                    for event_type in event_types:
                        if location != '':
                            break
                        if event_type.text not in creation_event_types:
                            continue

                        earliest_date = event.find('lido:eventDate/lido:date/lido:earliestDate', ns)
                        latest_date = event.find('lido:eventDate/lido:date/lido:latestDate', ns)
                        if earliest_date is not None:
                            creation_date_earliest = earliest_date.text
                            if creation_date_earliest is not None:
                                earliest_date_split = creation_date_earliest.split('.')
                                earliest_date_split.reverse()
                                while len(earliest_date_split[0]) < 4:
                                    earliest_date_split[0] = '0' + earliest_date_split[0]
                                if len(earliest_date_split) > 1:
                                    while len(earliest_date_split[1]) < 2:
                                        earliest_date_split[1] = '0' + earliest_date_split[1]
                                    if len(earliest_date_split) > 2:
                                        while len(earliest_date_split[2]) < 2:
                                            earliest_date_split[2] = '0' + earliest_date_split[2]
                                    creation_date_earliest = '.'.join(earliest_date_split)
                                if len(earliest_date_split) == 1:
                                    creation_date_earliest = earliest_date_split[0]
                        if latest_date is not None:
                            creation_date_latest = latest_date.text
                            if creation_date_latest is not None:
                                latest_date_split = creation_date_latest.split('.')
                                latest_date_split.reverse()
                                while len(latest_date_split[0]) < 4:
                                    latest_date_split[0] = '0' + latest_date_split[0]
                                if len(latest_date_split) > 1:
                                    while len(latest_date_split[1]) < 2:
                                        latest_date_split[1] = '0' + latest_date_split[1]
                                    if len(latest_date_split) > 2:
                                        while len(latest_date_split[2]) < 2:
                                            latest_date_split[2] = '0' + latest_date_split[2]
                                    creation_date_latest = '.'.join(latest_date_split)
                                if len(latest_date_split) == 1:
                                    creation_date_latest = latest_date_split[0]

                        places = event.findall('lido:eventPlace/lido:place', ns)
                        if places is not None:
                            for place in places:
                                place_appelation_value = place.find('lido:namePlaceSet/lido:appellationValue', ns)
                                if location != '':
                                    location += ', '
                                if place_appelation_value is not None:
                                    location += place_appelation_value.text

                                child = place.find('lido:partOfPlace', ns)
                                while child is not None:
                                    place_appelation_value = child.find('lido:namePlaceSet/lido:appellationValue', ns)
                                    if location != '':
                                        location += ', '
                                    if place_appelation_value is not None:
                                        location += place_appelation_value.text
                                    child = child.find('lido:partOfPlace', ns)

            source_url_find = rec.find(record_wrap + 'lido:recordInfoSet/lido:recordInfoLink', ns)
            source_url = source_url_find.text \
                if source_url_find is not None \
                else None

            identifier_find = rec.find(repository_wrap
                                       + 'lido:repositorySet/lido:workID', ns
                                       )
            identifier = identifier_find.text \
                if identifier_find is not None \
                else None

            image_url = rec.find(resource_wrap + 'lido:resourceSet/lido:'
                                 + 'resourceRepresentation/lido:linkResource', ns).text \
                if rec.find(resource_wrap + 'lido:resourceSet/lido:'
                            + 'resourceRepresentation/lido:linkResource', ns) is not None\
                else None

            image_extension = rec.find(resource_wrap + 'lido:resourceSet/lido:'
                                       + 'resourceRepresentation/lido:linkResource',
                                       ns).attrib['{' + ns['lido'] + '}formatResource'] \
                if rec.find(resource_wrap + 'lido:resourceSet/lido:'
                            + 'resourceRepresentation/lido:linkResource', ns) is not None\
                else None

            actors = rec.findall(actor_wrap + 'lido:actorInRole', ns)
            for actor in actors:
                term = actor.find('lido:roleActor/lido:term', ns)
                if term is not None and term.text == 'kujutatu':
                    muis_actor_id = int(actor.find("lido:actor/lido:actorID", ns).text)
                    names = actor.findall("lido:actor/lido:nameActorSet/lido:appellationValue", ns)
                    all_names = ''
                    main_name = ''
                    for name in names:
                        if name.attrib['{' + ns['lido'] + '}pref'] == 'preferred':
                            main_name_parts = name.text.split(',')
                            main_name = main_name_parts[-1].replace(' ', '')
                            if len(main_name_parts) > 1:
                                for part in main_name_parts[0:len(main_name_parts) - 1]:
                                    main_name += ' ' + part
                        all_names += (name.attrib['{' + ns['lido'] + '}label'] + ': ' + name.text + '. ').capitalize()

                    existing_album = Album.objects.filter(muis_person_ids__contains=[muis_actor_id]).first()
                    if existing_album is None:
                        person_album = Album(
                            name=main_name,
                            description=all_names,
                            muis_person_ids=[muis_actor_id],
                            atype=Album.PERSON
                        )
                        person_album.save()
                        person_album_ids.append(person_album.id)
                    else:
                        person_album_ids.append(existing_album.id)

            if image_url is not None:
                img_data = requests.get(image_url).content
                image_id = external_id.split(':')[-1]
                file_name = set_name + '_' + image_id + '.' + image_extension
                file_name = file_name.replace(':', '_')
                path = settings.MEDIA_ROOT + '/uploads/' + file_name
                with open(path, 'wb') as handler:
                    handler.write(img_data)
                photo = Photo(
                    image=path,
                    description=description,
                    source_key=identifier,
                    source_url=source_url,
                    external_id=external_id,
                    source=source
                )
                photo.save()

                photo = Photo.objects.get(id=photo.id)
                photo.image.name = 'uploads/' + file_name
                if location != '':
                    google_geocode_url = f'https://maps.googleapis.com/maps/api/geocode/json?' \
                                        f'address={location}' \
                                        f'&key={settings.UNRESTRICTED_GOOGLE_MAPS_API_KEY}'
                    google_response_json = requests.get(google_geocode_url).text
                    google_response_parsed = json.loads(google_response_json)
                    status = google_response_parsed.get('status', None)
                    if status == 'OK':
                        # Google was able to answer some geolocation for this description
                        address = google_response_parsed.get('results')[0].get('formatted_address')
                        lat_lng = google_response_parsed.get('results')[0].get('geometry').get('location')
                        photo.lat = lat_lng['lat']
                        photo.lon = lat_lng['lng']
                        photo.address = address

                        source_geotag = GeoTag(
                            lat=lat_lng['lat'],
                            lon=lat_lng['lng'],
                            origin=GeoTag.SOURCE,
                            type=GeoTag.SOURCE_GEOTAG,
                            map_type=GeoTag.NO_MAP,
                            photo=photo,
                            is_correct=True,
                            trustworthiness=0.07
                        )

                        source_geotag.save()
                        source_geotag = GeoTag.objects.filter(id=source_geotag.id).first()
                        photo.geotag_count = 1
                        photo.first_geotag = source_geotag.created
                        photo.latest_geotag = source_geotag.created

                if creation_date_latest is not None or creation_date_earliest is not None:
                    dating = Dating(photo=photo)
                    if creation_date_latest is not None and creation_date_earliest is not None:
                        if creation_date_earliest != creation_date_latest:
                            dating.raw = creation_date_earliest + '-' + creation_date_latest
                            dating.start_accuracy = creation_date_earliest.count('.')
                            dating.end_accuracy = creation_date_earliest.count('.')
                        else:
                            dating.raw = creation_date_earliest
                            dating.start_accuracy = creation_date_earliest.count('.')
                    elif creation_date_latest is not None:
                        dating.raw = creation_date_latest
                        dating.start_accuracy = creation_date_latest.count('.')
                    elif creation_date_earliest is not None:
                        dating.raw = creation_date_earliest
                        dating.start_accuracy = creation_date_earliest.count('.')
                    dating.save()
                    dating = Dating.objects.filter(id=dating.id).first()
                    photo.dating_count = 1
                    photo.first_dating = dating.created
                    photo.latest_dating = dating.created

                photo.light_save()
                photo.add_to_source_album()

                for album in albums:
                    if not album.cover_photo:
                        album.cover_photo = photo
                    ap = AlbumPhoto(photo=photo, album=album, type=AlbumPhoto.CURATED)
                    ap.save()

                person_albums = Album.objects.filter(id__in=person_album_ids)
                if person_albums is not None:
                    for album in person_albums:
                        if not album.cover_photo:
                            album.cover_photo = photo
                        ap = AlbumPhoto(photo=photo, album=album, type=AlbumPhoto.FACE_TAGGED)
                        ap.save()

                        all_person_album_ids_set.add(album.id)

        for album in albums:
            album.set_calculated_fields()
            album.save()

        all_person_album_ids = list(all_person_album_ids_set)
        all_person_albums = Album.objects.filter(id__in=all_person_album_ids)

        if all_person_albums is not None:
            for person_album in all_person_albums:
                person_album.set_calculated_fields()
                person_album.save()
