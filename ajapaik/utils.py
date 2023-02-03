import datetime as datetime
import hashlib
import os
from math import cos, sin, radians, atan2, sqrt

from PIL.Image import Image
from django.http import HttpRequest
from django.utils import timezone
from django.utils.translation import gettext as _


def get_etag(_request: HttpRequest, image: Image):
    if os.path.isfile(image):
        m = hashlib.md5()
        with open(image, 'rb') as f:
            m.update(f.read())
        return m.hexdigest()

    return None


def last_modified(_request: HttpRequest, image: Image) -> datetime.datetime | None:
    if os.path.isfile(image):
        return datetime.datetime.fromtimestamp(os.path.getmtime(image))

    return None


# FIXME: Ugly functions, make better or import from whatever library we have anyway
def calculate_thumbnail_size(p_width: int, p_height: int, desired_longest_side: int) -> tuple[int, int]:
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


def calculate_thumbnail_size_max_height(p_width: int, p_height: int, desired_height: int) -> tuple[int, int]:
    w = float(p_width)
    h = float(p_height)
    desired_height = float(desired_height)
    factor = h / desired_height
    desired_width = w / factor

    return int(desired_width), int(desired_height)


def convert_to_degrees(value: list[list[int]]):
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


def angle_diff(angle1: float, angle2: float):
    diff = angle2 - angle1
    if diff < -180:
        diff += 360
    elif diff > 180:
        diff -= 360
    return abs(diff)


def average_angle(angles: list[int]):
    x = y = 0
    for e in angles:
        x += cos(radians(e))
        y += sin(radians(e))
    return atan2(y, x)


def distance_in_meters(lon1, lat1, lon2, lat2):
    lat_coeff = cos(radians((lat1 + lat2) / 2.0))
    return (2 * 6350e3 * 3.1415 / 360) * sqrt((lat1 - lat2) ** 2 + ((lon1 - lon2) * lat_coeff) ** 2)


def most_frequent(lst: list[float]) -> float:
    counter = 0
    num = lst[0]
    uniques = list(set(lst))

    for i in uniques:
        current_frequency = lst.count(i)
        if current_frequency >= counter:
            counter = current_frequency
            num = i
    return num


def least_frequent(lst: list[float]) -> float:
    counter = None
    num = lst[0]
    uniques = list(set(lst))

    for i in uniques:
        current_frequency = lst.count(i)
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

    if all_suggestions:
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

    if new_value is None:
        return _('You must specify a new value when making a suggestion'), \
               photo_suggestions, was_action_successful, points

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

        if all_suggestions:
            suggestions = [new_value]

            for suggestion in all_suggestions:
                suggestions.append(getattr(suggestion, key))

            most_common_choice = most_frequent(suggestions)
            if new_value != most_common_choice:
                response = SUGGESTION_SAVED_BUT_CONSENSUS_NOT_AFFECTED
                was_action_successful = False
            new_value = most_common_choice

        if function_name:
            old_value = getattr(photo, key)
            if function_name == 'do_rotate' and (old_value is None or (new_value != old_value)):
                getattr(photo, function_name)(new_value)
            elif (function_name != 'do_rotate') and ((old_value or new_value is True) and old_value != new_value):
                getattr(photo, function_name)()
        else:
            setattr(photo, key, new_value)
            photo.save()

        if previous_suggestion:
            if response != SUGGESTION_SAVED_BUT_CONSENSUS_NOT_AFFECTED:
                response = SUGGESTION_CHANGED
                was_action_successful = True
        else:
            Points.objects.create(user=profile, action=action_type, photo=photo, points=score, created=timezone.now())
            if response != SUGGESTION_CHANGED and response != SUGGESTION_SAVED_BUT_CONSENSUS_NOT_AFFECTED:
                response = SUGGESTION_SAVED
                was_action_successful = True
                points = score

    return response, photo_suggestions, was_action_successful, points
