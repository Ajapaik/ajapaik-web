import datetime
import itertools
import json

import requests
import roman
from django.conf import settings

from ajapaik.ajapaik.models import Album, GeoTag, GoogleMapsReverseGeocode, Location, Photo, LocationPhoto, Dating

century_suffixes = [
    'saj x',
    ' saj x',
    '.saj x',
    ' .saj x',
    '.saj. x',
    '. saj.x',
    '. saj. x',
    ' .saj. x',
    'saj.x',
    'saj. x',
    ' saj.x',
    ' saj. x',
    'sajandi x',
    ' sajandi x',
    '.sajandi x',
    ' .sajandi x'
]

start_of_century_suffixes = [x.replace('x', 'algus') for x in century_suffixes]
end_of_century_suffixes = [x.replace('x', 'lõpp') for x in century_suffixes]
starts_of_century = [b + a for a in start_of_century_suffixes for b in map(str, list(range(1, 21)))]
ends_of_century = [b + a for a in end_of_century_suffixes for b in map(str, list(range(1, 21)))]


def unstructured_date_to_structured_date(date, all_date_prefixes, is_later_date):
    date = date.strip('.').strip().strip('.').strip()
    date = date.lower()

    if date in starts_of_century:
        if date[:2].isdigit():
            how_many_hundreds = int(date[:2])
        else:
            how_many_hundreds = int(date[:1])
        date = how_many_hundreds * 100
        if is_later_date:
            date += 25
        date = str(date)

    if date in ends_of_century:
        if date[:2].isdigit():
            how_many_hundreds = int(date[:2])
        else:
            how_many_hundreds = int(date[:1])
        date = how_many_hundreds * 100
        if not is_later_date:
            date -= 25
        date = str(date)

    date = date.replace('0ndate algus', '5')
    date = date.replace('0-ndate algus', '5')
    date = date.replace('vahemikus ', '', 1)
    if ' või ' in date:
        date = date.replace(' või ', '-')
    if date.endswith('.a.?'):
        date = date.replace('.a.?', '')
        if date.isdigit():
            date = f'umbes.{date}'
    date = date.strip().strip('.').strip().strip('.')
    irregular_decade_suffixes = [
        '-ndad aastad', "'ndad", '-ndad a', '.dad', '. aastad', ' aastad', 'ndad', '-dad', 'a-d'
    ]
    for suffix in irregular_decade_suffixes:
        if date.endswith(suffix):
            date = date.replace(suffix, '.aastad')
            break

    irregular_approximate_date_prefixes = [
        'u. ', 'u.', 'u ', 'ca. ', 'ca.', 'ca ', 'ca', 'arvatavasti. ', 'arvatavasti.', 'arvatavasti'
    ]
    for prefix in irregular_approximate_date_prefixes:
        if date.startswith(prefix):
            date = date.replace(prefix, 'umbes.', 1)
            break

    months = [
        ('jaanuar', '1'),
        ('jaan', '1'),
        ('veebruar', '2'),
        ('veebr', '2'),
        ('veeb', '2'),
        ('märts', '3'),
        ('aprill', '4'),
        ('apr', '4'),
        ('mai', '5'),
        ('juuni', '6'),
        ('juuli', '7'),
        ('august', '8'),
        ('aug', '8'),
        ('september', '9'),
        ('sept', '9'),
        ('sep', '9'),
        ('oktoober', '10'),
        ('okt', '10'),
        ('november', '11'),
        ('nov', '11'),
        ('detsember', '12'),
        ('dets', '12')
    ]

    month_name_fixed = False
    for month in months:
        if month_name_fixed:
            break
        if date.endswith(f'. {month[0]}'):
            date = date.replace(f'. {month[0]}', '')
            date = f'{month[1]}.{date}'
            month_name_fixed = True
        elif date.endswith(f'.{month[0]}'):
            date = date.replace(f'.{month[0]}', '')
            date = f'{month[1]}.{date}'
            month_name_fixed = True
        elif date.endswith(f' .{month[0]}'):
            date = date.replace(f' .{month[0]}', '')
            date = f'{month[1]}.{date}'
            month_name_fixed = True
        elif date.endswith(f' {month[0]}'):
            date = date.replace(f' {month[0]}', '')
            date = f'{month[1]}.{date}'
            month_name_fixed = True

    for month in months:
        if month_name_fixed:
            break
        if date.startswith(f'{month[0]}. '):
            date = date.replace(f'{month[0]}. ', '')
            date = f'{month[1]}.{date}'
            break
        elif date.startswith(f'{month[0]}.'):
            date = date.replace(f'{month[0]}.', '')
            date = f'{month[1]}.{date}'
            break
        elif date.startswith(month[0]):
            date = date.replace(month[0], '')
            date = f'{month[1]}.{date}'
            break

    seasons = [
        ('talv', ['1.12', '28.2']),
        ('kevad', ['1.3', '31.5']),
        ('suvi', ['1.6', '31.8']),
        ('sügis', ['1.9', '31.12'])
    ]

    for season in seasons:
        if date.startswith(season[0]):
            date = date.replace(season[0], '')
            date = date.strip('.').strip().strip('.').strip()
            if is_later_date:
                date = f'{season[1][1]}.{date}'
            else:
                date = f'{season[1][0]}.{date}'

    date = date.replace('..', '.')
    dash_split_date = date.split('-')
    if len(dash_split_date) > 1:
        if is_later_date:
            date = dash_split_date[1]
            date = date.strip('.').strip().strip('.').strip('')
            if date.endswith('.aastad'):
                date = date.replace('.aastad', '')
                if len(date) < 3:
                    if len(dash_split_date[0]) > 3:
                        if int(dash_split_date[0][2:4]) < int(date):
                            date = dash_split_date[0][0:2] + date
                        else:
                            date = str(int(dash_split_date[0][0:2]) + 1) + date
                date = str(int(date) + 10)
        else:
            date = dash_split_date[0]
            date = date.strip('.').strip().strip('.').strip('')

    date = date.replace('..', '.')
    for prefix in all_date_prefixes:
        if date.startswith(prefix) and not date.startswith(f'{prefix}.'):
            date = date.replace(prefix, f'{prefix}.', 1)
            break

    quarter_century = 'veerand'
    if quarter_century in date:
        split_date = date.split(quarter_century)
        number = roman.fromRoman(split_date[0].strip('.').strip().strip('.').strip('').upper())
        year_hundred = split_date[1].strip('.').strip().strip('.').strip('')
        if not is_later_date:
            number -= 1
        date = int(year_hundred) + int(number) * 25
        date = str(date)

    decade = 'kümnend'
    if decade in date:
        split_date = date.split(decade)
        number = roman.fromRoman(split_date[0].strip('.').strip().strip('.').strip('').upper())
        year_hundred = split_date[1].strip('.').strip().strip('.').strip('')
        date = int(year_hundred) + int(number) * 10
        if is_later_date:
            date += 10
        date = str(date)

    date = date.replace('..', '.')
    date = date.replace('. ', '.')
    date = date.replace(' .', '.')

    return date


def set_text_fields_from_muis(photo, rec, object_description_wraps, ns):
    dating = None
    muis_description_field_mapping = {
        'sisu kirjeldus': 'description',
        'kommentaar': 'muis_comment',
        'pealkiri': 'muis_title',
        '<legendid ja kirjeldused>': 'muis_legends_and_descriptions',
        'tekst objektil': 'muis_text_on_object',
    }

    for value in muis_description_field_mapping.values():
        photo = reset_photo_translated_field(photo, value)

    description_finds = rec.findall(object_description_wraps, ns)

    for description_element in description_finds:
        description_type_element = description_element.find('lido:sourceDescriptiveNote', ns)
        if description_type_element is None:
            continue

        description_type = description_type_element.text
        description_text_element = description_element.find('lido:descriptiveNoteValue', ns)
        description_text = description_text_element.text

        if description_type in muis_description_field_mapping:
            if description_type == 'sisu kirjeldus':
                photo.description_original_language = None
            elif description_type == 'dateering':
                dating = description_text
            else:
                setattr(photo, muis_description_field_mapping[description_type], description_text)

    photo.light_save()

    return photo, dating


def reset_photo_translated_field(photo, attribute_name, attribute_value=None):
    photo = Photo.objects.get(id=photo.id)
    detection_lang = 'et'

    setattr(photo, attribute_name, attribute_value)
    for language in settings.MODELTRANSLATION_LANGUAGES:
        if language == detection_lang:
            setattr(photo, f'{attribute_name}_{language}', attribute_value)
        else:
            setattr(photo, f'{attribute_name}_{language}', None)

    photo.light_save()

    return photo


def extract_dating_from_event(
        events,
        locations,
        creation_date_earliest,
        creation_date_latest,
        skip_dating,
        ns
):
    duplicate_event_type = 'kopeerimine (valmistamine)'
    creation_event_types = ['valmistamine', '<valmistamine/tekkimine>', 'pildistamine', 'sõjandus ja kaitse', 'sõjad']
    date_prefix_earliest = None
    date_prefix_latest = None
    latest_had_decade_suffix = False

    for event in events:
        event_types = event.findall('lido:eventType/lido:term', ns)

        for event_type in event_types:
            if event_type.text == duplicate_event_type:
                break
            if event_type.text not in creation_event_types:
                continue

            if not skip_dating:
                earliest_date = event.find('lido:eventDate/lido:date/lido:earliestDate', ns)
                latest_date = event.find('lido:eventDate/lido:date/lido:latestDate', ns)

                if earliest_date is not None and earliest_date.text:
                    creation_date_earliest, date_prefix_earliest, _, \
                        = get_muis_date_and_prefix(
                        earliest_date.text, False
                    )

                if latest_date is not None and latest_date.text:
                    creation_date_latest, date_prefix_latest, latest_had_decade_suffix, \
                        = get_muis_date_and_prefix(
                        latest_date.text, True
                    )

            places = event.findall('lido:eventPlace/lido:place', ns)

            def _get_place_entity(place):
                new_locations = []
                entity_type = place.attrib[f"{{{ns['lido']}}}politicalEntity"]

                if entity_type is None:
                    entity_type = place.attrib[f"{{{ns['lido']}}}geographicalEntity"]

                place_appellation_value = place.find('lido:namePlaceSet/lido:appellationValue', ns)
                if place_appellation_value is not None:
                    new_locations.append((place_appellation_value.text, entity_type))

                child = place.find('lido:partOfPlace', ns)

                return new_locations, child

            if places:
                for place in places:
                    new_locations, child = get_place_entity(place)
                    locations.extend(new_locations)

                    while child is not None:
                        new_locations, child
                        locations.extend(new_locations)

    return locations, creation_date_earliest, creation_date_latest, date_prefix_earliest, date_prefix_latest, latest_had_decade_suffix


def add_person_albums(actors, person_album_ids, ns):
    author = None

    for actor in actors:
        term = actor.find('lido:roleActor/lido:term', ns)
        if term is None:
            continue

        if term.text in ['kujutatu', 'autor']:
            names = actor.findall("lido:actor/lido:nameActorSet/lido:appellationValue", ns)
            main_name = ''
            all_names = ''

            for name in names:
                if name.attrib[f"{{{ns['lido']}}}pref"] == 'preferred':
                    main_name_parts = name.text.split(',')
                    main_name = main_name_parts[-1].strip()

                    if len(main_name_parts) > 1:
                        for part in main_name_parts[0:len(main_name_parts) - 1]:
                            main_name += f' {part}'

                label = name.attrib[f"{{{ns['lido']}}}label"]
                all_names += f"{label}: {name.text}. ".capitalize()

            if term.text == 'autor':
                author = main_name
                continue

            existing_album = Album.objects.filter(name=main_name, atype=Album.PERSON).first()
            muis_actor_wrapper = actor.find("lido:actor/lido:actorID", ns)

            if muis_actor_wrapper is not None:
                muis_actor_id = int(muis_actor_wrapper.text)

            if existing_album:
                if muis_actor_id:
                    existing_album.muis_person_ids = [*existing_album.muis_person_ids, muis_actor_id]
                    existing_album.save(update_fields=['muis_person_ids'])

                person_album_ids.append(existing_album.id)
                continue

            person_album = Album(
                name=main_name,
                description=all_names,
                atype=Album.PERSON,
                muis_person_ids=[muis_actor_id] if muis_actor_id else []
            )
            person_album.light_save()
            person_album_ids.append(person_album.id)

    return person_album_ids, author


def get_muis_date_and_prefix(date, is_later_date):
    date_prefix = None
    had_decade_suffix = False
    approximate_date_prefixes = ['ligikaudu', 'arvatav aeg', 'umbes']
    before_date_prefix = 'enne'
    after_date_prefix = 'pärast'
    all_date_prefixes = approximate_date_prefixes + [before_date_prefix, after_date_prefix]
    date = unstructured_date_to_structured_date(date, all_date_prefixes, is_later_date)

    if date is None:
        return date, date_prefix, had_decade_suffix

    decade_suffix = 'aastad'
    earliest_date_split = date.split('.')
    index = 0

    for split in earliest_date_split:
        earliest_date_split[index] = split.strip()
        index += 1

    if earliest_date_split[-1] == decade_suffix:
        had_decade_suffix = True

    if earliest_date_split[0] in all_date_prefixes:
        date_prefix = earliest_date_split[0]
        earliest_date_split = earliest_date_split[1:]

    earliest_date_split.reverse()

    while len(earliest_date_split[0]) < 4:
        earliest_date_split[0] = f'0{earliest_date_split[0]}'

    if len(earliest_date_split) > 1:
        while len(earliest_date_split[1]) < 2:
            earliest_date_split[1] = f'0{earliest_date_split[1]}'
        if len(earliest_date_split) > 2:
            while len(earliest_date_split[2]) < 2:
                earliest_date_split[2] = f'0{earliest_date_split[2]}'
        date = '.'.join(earliest_date_split)

    if len(earliest_date_split) == 1:
        date = earliest_date_split[0]

    if date_prefix in approximate_date_prefixes:
        date = f'({date})'

    return date, date_prefix, had_decade_suffix


def add_geotag_from_address_to_photo(photo, locations):
    locations.sort()
    locations = list(locations for locations, _ in itertools.groupby(locations))
    for location in locations:
        search_string = ''
        parent_location_object = None

        for sublocation in location:
            location_objects = \
                Location.objects.filter(name=sublocation[0], location_type=sublocation[1])
            if parent_location_object is not None:
                location_objects = location_objects.filter(sublocation_of=parent_location_object)
            location_object = location_objects.first()
            if location_object is None:
                location_object = Location(name=sublocation[0], location_type=sublocation[1])
                if parent_location_object is not None:
                    location_object.sublocation_of = parent_location_object
                location_object.save()
                location_object = Location.objects.filter(id=location_object.id).first()

            location_photo = LocationPhoto.objects.filter(location=location_object, photo=photo).first()
            if location_photo is None:
                location_photo = LocationPhoto(location=location_object, photo=photo)
                location_photo.save()
            if search_string != '':
                search_string += ', '
            search_string += sublocation[0]
            parent_location_object = location_object

    if location_object.google_reverse_geocode:
        lat = location_object.google_reverse_geocode.lat
        lon = location_object.google_reverse_geocode.lon
        address = location_object.google_reverse_geocode.response.get('results')[0].get('formatted_address')
    else:
        # $$$ in the start and end of text signifies unstructured data (coordinates, instructions about location, etc.)
        search_string = search_string.strip("$ ")
        google_geocode_url = f'https://maps.googleapis.com/maps/api/geocode/json?' \
                             f'address={search_string}' \
                             f'&key={settings.UNRESTRICTED_GOOGLE_MAPS_API_KEY}'
        google_response_json = requests.get(google_geocode_url).text
        google_response_parsed = json.loads(google_response_json)
        status = google_response_parsed.get('status', None)

        if not status == 'OK':
            return photo

        # Google was able to answer some geolocation for this description
        address = google_response_parsed.get('results')[0].get('formatted_address')
        lat_lng = google_response_parsed.get('results')[0].get('geometry').get('location')

        if not lat_lng:
            return photo

        lat = lat_lng['lat']
        lon = lat_lng['lng']
        google_maps_reverse_geocode = GoogleMapsReverseGeocode(lat=lat, lon=lon, response=google_response_parsed)
        google_maps_reverse_geocode.save()
        location_object.google_reverse_geocode = google_maps_reverse_geocode
        location_object.save()

    if photo.lat is None:
        photo.lat = lat
    if photo.lon is None:
        photo.lon = lon
    if photo.address is None:
        photo.address = address

    source_geotag = GeoTag(
        lat=lat,
        lon=lon,
        origin=GeoTag.SOURCE,
        type=GeoTag.SOURCE_GEOTAG,
        map_type=GeoTag.NO_MAP,
        photo=photo,
        is_correct=False,
        trustworthiness=0
    )
    source_geotag.save()
    source_geotag = GeoTag.objects.filter(id=source_geotag.id).first()

    if photo.geotag_count is None:
        photo.geotag_count = 1
    else:
        photo.geotag_count += 1
    if photo.first_geotag is None:
        photo.first_geotag = source_geotag.created
    photo.latest_geotag = source_geotag.created

    return photo


def raw_date_to_date(raw_date):
    raw_date_stripped = raw_date.replace(')', '').replace('(', '').replace('-', '').strip('.')
    raw_date_split = raw_date_stripped.split('.')
    dating_start_day = 1
    dating_start_month = 1
    dating_start_year = 1
    if len(raw_date_split) > 0:
        dating_start_year = int(raw_date_split[0])
    if len(raw_date_split) > 1:
        dating_start_month = int(raw_date_split[1])
    if len(raw_date_split) > 2:
        dating_start_day = int(raw_date_split[2])
    date = datetime.date(dating_start_year, dating_start_month, dating_start_day)
    return date


def add_dating_to_photo(photo, earliest_date, latest_date, date_prefix_earliest, date_prefix_latest,
                        date_latest_has_suffix):
    if latest_date is None and earliest_date is None:
        return photo

    if earliest_date is not None:
        earliest_date = earliest_date.replace('aastad', '').strip('.')
    if latest_date is not None:
        latest_date = latest_date.replace('aastad', '').strip('.')

    before_date_prefix = 'enne'
    after_date_prefix = 'pärast'
    approximate_date_prefixes = ['ligikaudu', 'arvatav aeg', 'umbes']
    dating = Dating(photo=photo)
    if date_latest_has_suffix:
        latest_date = str(int(latest_date) + 10)

    if date_prefix_earliest in approximate_date_prefixes:
        dating.start_approximate = True
    if date_prefix_latest in approximate_date_prefixes:
        dating.end_approximate = True
    if latest_date is not None and earliest_date is not None:
        if earliest_date != latest_date:
            dating.raw = f'{earliest_date}-{latest_date}'
            dating.start_accuracy = earliest_date.count('.')
            dating.end_accuracy = earliest_date.count('.')
        else:
            dating.raw = earliest_date
            dating.start_accuracy = earliest_date.count('.')
    elif latest_date is not None:
        dating.raw = latest_date
        dating.start_accuracy = latest_date.count('.')
    elif earliest_date is not None:
        dating.raw = earliest_date
        dating.start_accuracy = earliest_date.count('.')

    if dating.raw is not None and (latest_date is None or earliest_date is None) or (latest_date == earliest_date):
        if before_date_prefix in [date_prefix_earliest, date_prefix_latest]:
            dating.raw = f'-{dating.raw}'
        if after_date_prefix in [date_prefix_earliest, date_prefix_latest]:
            dating.raw += '-'

    if earliest_date is not None:
        dating.start = raw_date_to_date(earliest_date)
    if latest_date is not None:
        if earliest_date == latest_date and date_latest_has_suffix:
            latest_date = str(int(latest_date) + 10)
        dating.end = raw_date_to_date(latest_date)

    dating.save()
    dating = Dating.objects.filter(id=dating.id).first()
    photo.dating_count = 1
    if photo.dating_count < 1:
        photo.first_dating = dating.created
    photo.dating_count += 1
    photo.latest_dating = dating.created
    photo.save(update_fields=['dating_count', 'latest_dating'])
    return photo
