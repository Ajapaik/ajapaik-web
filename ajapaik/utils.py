import hashlib
import itertools
import os
import requests
import json

from math import cos, sin, radians, atan2, sqrt

from googletrans import Translator
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.conf import settings
import datetime


def get_etag(_request, image, _content):
    if os.path.isfile(image):
        m = hashlib.md5()
        with open(image, 'rb') as f:
            m.update(f.read())
        return m.hexdigest()

    return None


def last_modified(_request, image, _content):
    from datetime import datetime
    if os.path.isfile(image):
        return datetime.fromtimestamp(os.path.getmtime(image))

    return None


# FIXME: Ugly functions, make better or import from whatever library we have anyway
def calculate_thumbnail_size(p_width, p_height, desired_longest_side):
    if p_width and p_height:
        w = float(p_width)
        h = float(p_height)
        desired_longest_side = float(desired_longest_side)
        if w > h:
            desired_width = desired_longest_side
            factor = w / desired_longest_side
            desired_height = h / factor
        else:
            desired_height = desired_longest_side
            factor = h / desired_longest_side
            desired_width = w / factor
    else:
        return 400, 300

    return int(desired_width), int(desired_height)


def calculate_thumbnail_size_max_height(p_width, p_height, desired_height):
    w = float(p_width)
    h = float(p_height)
    desired_height = float(desired_height)
    factor = h / desired_height
    desired_width = w / factor

    return int(desired_width), int(desired_height)


def convert_to_degrees(value):
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)

    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)

    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)


def angle_diff(angle1, angle2):
    diff = angle2 - angle1
    if diff < -180:
        diff += 360
    elif diff > 180:
        diff -= 360
    return abs(diff)


def average_angle(angles):
    x = y = 0
    for e in angles:
        x += cos(radians(e))
        y += sin(radians(e))
    return atan2(y, x)


def distance_in_meters(lon1, lat1, lon2, lat2):
    lat_coeff = cos(radians((lat1 + lat2) / 2.0))
    return (2 * 6350e3 * 3.1415 / 360) * sqrt((lat1 - lat2) ** 2 + ((lon1 - lon2) * lat_coeff) ** 2)


def most_frequent(List):
    counter = 0
    num = List[0]
    uniques = list(set(List))

    for i in uniques:
        current_frequency = List.count(i)
        if (current_frequency >= counter):
            counter = current_frequency
            num = i
    return num


def least_frequent(List):
    counter = None
    num = List[0]
    uniques = list(set(List))

    for i in uniques:
        current_frequency = List.count(i)
        if not counter or current_frequency < counter:
            counter = current_frequency
            num = i

    return num


def can_action_be_done(model, photo, profile, key, new_value):
    new_suggestion = model(proposer=profile, photo=photo)
    setattr(new_suggestion, key, new_value)

    all_suggestions = model.objects.filter(
            photo=photo
        ).exclude(
            proposer=profile
        ).order_by(
            'proposer_id',
            '-created'
        ).all().distinct(
            'proposer_id'
        )

    if all_suggestions is not None:
        suggestions = [new_value]

        for suggestion in all_suggestions:
            suggestions.append(getattr(suggestion, key))

        most_common_choice = most_frequent(suggestions)
        return new_value == most_common_choice
    else:
        return True


def suggest_photo_edit(photo_suggestions, key, new_value, Points, score, action_type, model, photo, profile,
                       response, function_name):
    was_action_successful = True
    points = 0
    SUGGESTION_ALREADY_SUGGESTED = _('You have already submitted this suggestion')
    SUGGESTION_CHANGED = _('Your suggestion has been changed')
    SUGGESTION_SAVED = _('Your suggestion has been saved')
    SUGGESTION_SAVED_BUT_CONSENSUS_NOT_AFFECTED = _('Your suggestion has been saved, but previous consensus remains')
    if new_value is not None:
        previous_suggestion = model.objects.filter(photo=photo, proposer=profile).order_by('-created').first()
        if previous_suggestion and getattr(previous_suggestion, key) == new_value:
            if response != SUGGESTION_CHANGED and response != SUGGESTION_SAVED \
                    and response != SUGGESTION_SAVED_BUT_CONSENSUS_NOT_AFFECTED:
                response = SUGGESTION_ALREADY_SUGGESTED
                was_action_successful = False
        else:
            new_suggestion = model(proposer=profile, photo=photo)
            setattr(new_suggestion, key, new_value)
            photo_suggestions.append(new_suggestion)
            all_suggestions = model.objects.filter(photo=photo).exclude(proposer=profile) \
                .order_by('proposer_id', '-created').all().distinct('proposer_id')

            if all_suggestions is not None:
                suggestions = [new_value]

                for suggestion in all_suggestions:
                    suggestions.append(getattr(suggestion, key))

                most_common_choice = most_frequent(suggestions)
                if new_value != most_common_choice:
                    response = SUGGESTION_SAVED_BUT_CONSENSUS_NOT_AFFECTED
                    was_action_successful = False
                new_value = most_common_choice

            if function_name is not None:
                old_value = getattr(photo, key)
                if function_name == 'do_rotate' and (old_value is None or (new_value != old_value)):
                    getattr(photo, function_name)(new_value)
                elif (function_name != 'do_rotate') and (
                        (old_value or new_value is True) and old_value != new_value):
                    getattr(photo, function_name)()
            else:
                setattr(photo, key, new_value)
                photo.save()

            if previous_suggestion:
                if response != SUGGESTION_SAVED_BUT_CONSENSUS_NOT_AFFECTED:
                    response = SUGGESTION_CHANGED
                    was_action_successful = True
            else:
                Points(user=profile, action=action_type, photo=photo, points=score, created=timezone.now()).save()
                if response != SUGGESTION_CHANGED and response != SUGGESTION_SAVED_BUT_CONSENSUS_NOT_AFFECTED:
                    response = SUGGESTION_SAVED
                    was_action_successful = True
                    points = score

    return response, photo_suggestions, was_action_successful, points


def add_geotag_from_address_to_photo(photo, locations, GeoTag, Location, LocationPhoto):
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

            Location(name=sublocation[0], location_type=sublocation[1])
            location_photo = LocationPhoto.objects.filter(location=location_object, photo=photo).first()
            if location_photo is None:
                location_photo = LocationPhoto(location=location_object, photo=photo)
                location_photo.save()
            if search_string != '':
                search_string += ', '
            search_string += sublocation[0]
            parent_location_object = location_object

        google_geocode_url = f'https://maps.googleapis.com/maps/api/geocode/json?' \
            f'address={search_string}' \
            f'&key={settings.UNRESTRICTED_GOOGLE_MAPS_API_KEY}'
        google_response_json = requests.get(google_geocode_url).text
        google_response_parsed = json.loads(google_response_json)
        status = google_response_parsed.get('status', None)
        lat_lng = None
        if status == 'OK':
            # Google was able to answer some geolocation for this description
            address = google_response_parsed.get('results')[0].get('formatted_address')
            lat_lng = google_response_parsed.get('results')[0].get('geometry').get('location')
        if lat_lng is not None:
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


def add_dating_to_photo(photo, earliest_date, latest_date, date_prefix_earliest, date_prefix_latest, Dating,
                        date_earliest_has_suffix, date_latest_has_suffix, earliest_had_beginning_of_century_suffix,
                        latest_had_beginning_of_century_suffix):
    if latest_date is not None or earliest_date is not None:
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
                dating.raw = earliest_date + '-' + latest_date
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

        if dating.raw is not None and (latest_date is None or earliest_date is None):
            if date_prefix_earliest == before_date_prefix:
                dating.raw = '-' + dating.raw
            if date_prefix_earliest == after_date_prefix:
                dating.raw += '-'
            if date_prefix_latest == before_date_prefix:
                dating.raw = '-' + dating.raw
            if date_prefix_latest == after_date_prefix:
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
    return photo


def get_muis_date_and_prefix(date):
    approximate_date_prefixes = ['ligikaudu', 'arvatav aeg', 'umbes']
    before_date_prefix = 'enne'
    after_date_prefix = 'pärast'
    all_date_prefixes = approximate_date_prefixes + [before_date_prefix, after_date_prefix]
    beginning_of_century_suffix = 'saj algusaastad'
    decade_suffix = 'aastad'
    date_prefix = None
    had_beginning_of_century_suffix = False
    had_decade_suffix = False
    if date is not None:
        earliest_date_split = date.split('.')
        if earliest_date_split[-1] == beginning_of_century_suffix:
            had_beginning_of_century_suffix = True
        if earliest_date_split[-1] == decade_suffix:
            had_decade_suffix = True
        if earliest_date_split[0] in all_date_prefixes:
            date_prefix = earliest_date_split[0]
            earliest_date_split = earliest_date_split[1:]
        earliest_date_split.reverse()
        while len(earliest_date_split[0]) < 4:
            earliest_date_split[0] = '0' + earliest_date_split[0]
        if len(earliest_date_split) > 1:
            while len(earliest_date_split[1]) < 2:
                earliest_date_split[1] = '0' + earliest_date_split[1]
            if len(earliest_date_split) > 2:
                while len(earliest_date_split[2]) < 2:
                    earliest_date_split[2] = '0' + earliest_date_split[2]
            date = '.'.join(earliest_date_split)
        if len(earliest_date_split) == 1:
            date = earliest_date_split[0]

        if date_prefix in approximate_date_prefixes:
            date = '(' + date + ')'
    return date, date_prefix, had_decade_suffix, had_beginning_of_century_suffix


def add_person_albums(actors, person_album_ids, Album, ns):
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

            existing_album = Album.objects.filter(name=main_name, atype=Album.PERSON).first()
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
    return person_album_ids


def extract_dating_from_event(
            events,
            location,
            creation_date_earliest,
            creation_date_latest,
            skip_dating,
            ns
        ):
    creation_event_types = ['valmistamine', '<valmistamine/tekkimine>', 'pildistamine', 'sõjandus ja kaitse', 'sõjad']
    date_prefix_earliest = None
    date_prefix_latest = None
    earliest_had_decade_suffix = False
    latest_had_decade_suffix = False
    earliest_had_beginning_of_century_suffix = False
    latest_had_beginning_of_century_suffix = False
    for event in events:
        event_types = event.findall('lido:eventType/lido:term', ns)
        if event_types is None:
            continue
        for event_type in event_types:
            if event_type.text not in creation_event_types:
                continue

            if not skip_dating:
                earliest_date = event.find('lido:eventDate/lido:date/lido:earliestDate', ns)
                latest_date = event.find('lido:eventDate/lido:date/lido:latestDate', ns)

                if earliest_date is not None and earliest_date.text is not None:
                    creation_date_earliest, date_prefix_earliest, earliest_had_decade_suffix, \
                        earliest_had_beginning_of_century_suffix = get_muis_date_and_prefix(
                            earliest_date.text
                        )

                if latest_date is not None and latest_date.text is not None:
                    creation_date_latest, date_prefix_latest, latest_had_decade_suffix, \
                        latest_had_beginning_of_century_suffix = get_muis_date_and_prefix(
                            latest_date.text
                        )

            places = event.findall('lido:eventPlace/lido:place', ns)
            if places is not None:
                new_location = []
                for place in places:
                    entity_type = place.attrib['{' + ns['lido'] + '}politicalEntity']
                    if entity_type is None:
                        entity_type = place.attrib['{' + ns['lido'] + '}geographicalEntity']
                    place_appelation_value = place.find('lido:namePlaceSet/lido:appellationValue', ns)
                    if place_appelation_value is not None:
                        new_location.append((place_appelation_value.text, entity_type))

                    child = place.find('lido:partOfPlace', ns)
                    while child is not None:
                        entity_type = child.attrib['{' + ns['lido'] + '}politicalEntity']
                        if entity_type is None:
                            entity_type = child.attrib['{' + ns['lido'] + '}geographicalEntity']
                        place_appelation_value = child.find('lido:namePlaceSet/lido:appellationValue', ns)
                        if place_appelation_value is not None:
                            new_location.append((place_appelation_value.text, entity_type))
                        child = child.find('lido:partOfPlace', ns)
                if new_location != []:
                    location.append(new_location)
    return location, creation_date_earliest, creation_date_latest, date_prefix_earliest, date_prefix_latest, \
        earliest_had_decade_suffix, latest_had_decade_suffix, earliest_had_beginning_of_century_suffix, \
        latest_had_beginning_of_century_suffix


def reset_modeltranslated_field(photo, attribute_value, attribute_name):
    translator = Translator()
    detection_lang = None
    if attribute_value is not None:
        attribute_value = "Test"
        if 2 == 3:
            detection = translator.detect(attribute_value)
            try:
                setattr(photo, attribute_name + '_' + detection.lang, attribute_value)
            except Exception as e:
                print(e)
            detection_lang = detection.lang
        detection_lang = 'et'
    for language in settings.MODELTRANSLATION_LANGUAGES:
        if language == detection_lang:
            continue
        else:
            setattr(photo, attribute_name + '_' + language, None)
    return photo


def set_text_fields_from_muis(photo, dating, rec, object_description_wraps, ns):
    muis_description_field_pairs = {
        'sisu kirjeldus': 'description',
        'kommentaar': 'muis_comment',
        'pealkiri': 'muis_title',
        '<legendid ja kirjeldused>': 'muis_legends_and_descriptions',
        'tekst objektil': 'muis_text_on_object',
        'dateering': None
    }

    description_finds = rec.findall(object_description_wraps, ns)
    for description_element in description_finds:
        reset_modeltranslated_field(photo, None, 'description')
        description_text_element = description_element.find('lido:descriptiveNoteValue', ns)
        description_type_element = description_element.find('lido:sourceDescriptiveNote', ns)
        description_text = description_text_element.text
        if description_type_element is None:
            continue
        description_type = description_type_element.text
        if description_type in muis_description_field_pairs:
            if description_type == 'sisu kirjeldus':
                reset_modeltranslated_field(photo, description_text, 'description')
                photo.description_original_language = None
            elif description_type == 'dateering':
                dating = description_text
            else:
                setattr(photo, muis_description_field_pairs[description_type], description_text)
    return photo, dating
