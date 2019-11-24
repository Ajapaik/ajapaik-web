import json
from django.http import QueryDict
from django.utils import timezone


DELETION_EXPIRATION_THRESHOLD_IN_HOURS = 24

GENDER_FEMALE = 0
GENDER_MALE = 1
GENDER_NOT_SURE = 2

GENDER_STRING_FEMALE = 'FEMALE'
GENDER_STRING_MALE = 'MALE'
GENDER_STRING_UNSURE = 'UNSURE'

AGE_CHILD = 0
AGE_ADULT = 1
AGE_ELDERLY = 2
AGE_NOT_SURE = 3

AGE_STRING_CHILD = 'CHILD'
AGE_STRING_ADULT = 'ADULT'
AGE_STRING_ELDERLY = 'ELDERLY'
AGE_STRING_UNSURE = 'UNSURE'


def is_value_present(val):
    return val is not None and len(val) > 0


def parse_parameter(parameter):
    if is_value_present(parameter):
        return int(parameter)

    return 0


def convert_to_query_dictionary(dictionary):
    query_dictionary = QueryDict('', mutable=True)
    query_dictionary.update(dictionary)
    return query_dictionary


def transform_annotation_queryset(user_id, query_set, transform_function):
    transformed_collection = []

    for entry in query_set:
        transformed_collection.append(json.dumps(transform_function(entry, user_id).__dict__))

    return transformed_collection


def is_annotation_deletable(user_id: int, created_on, created_by_id: int):
    global DELETION_EXPIRATION_THRESHOLD_IN_HOURS

    current_time = timezone.now()
    time_difference = current_time - created_on
    time_difference_in_hours = time_difference.total_seconds() / 3600

    return user_id == created_by_id and time_difference_in_hours <= DELETION_EXPIRATION_THRESHOLD_IN_HOURS


def parse_boolean(value):
    if is_value_present(value):
        return value in ['True', 'true']

    return None


def parse_gender_parameter(gender):
    global GENDER_MALE
    global GENDER_FEMALE
    global GENDER_NOT_SURE

    global GENDER_STRING_FEMALE
    global GENDER_STRING_MALE

    if gender is not None and gender.isdigit():
        return gender

    if gender == GENDER_STRING_MALE:
        return GENDER_MALE

    if gender == GENDER_STRING_FEMALE:
        return GENDER_FEMALE

    return GENDER_NOT_SURE


def parse_age_parameter(age):
    global AGE_ADULT
    global AGE_CHILD
    global AGE_ELDERLY
    global AGE_NOT_SURE

    global AGE_STRING_CHILD
    global AGE_STRING_ADULT
    global AGE_STRING_ELDERLY

    if age is not None and age.isdigit():
        return age

    if age == AGE_STRING_CHILD:
        return AGE_CHILD

    if age == AGE_STRING_ADULT:
        return AGE_ADULT

    if age == AGE_STRING_ELDERLY:
        return AGE_ELDERLY

    return AGE_NOT_SURE


def parse_age_to_constant(age):
    global AGE_ADULT
    global AGE_CHILD
    global AGE_ELDERLY
    global AGE_NOT_SURE

    global AGE_STRING_ADULT
    global AGE_STRING_CHILD
    global AGE_STRING_ELDERLY
    global AGE_STRING_UNSURE

    if age is None:
        return age

    if age == AGE_CHILD:
        return AGE_STRING_CHILD

    if age == AGE_ADULT:
        return AGE_STRING_ADULT

    if age == AGE_ELDERLY:
        return AGE_STRING_ELDERLY

    return AGE_STRING_UNSURE


def parse_gender_to_constant(gender):
    global GENDER_MALE
    global GENDER_FEMALE
    global GENDER_NOT_SURE

    global GENDER_STRING_MALE
    global GENDER_STRING_FEMALE
    global GENDER_STRING_UNSURE

    if gender is None:
        return gender

    if gender == GENDER_MALE:
        return GENDER_STRING_MALE

    if gender == GENDER_FEMALE:
        return GENDER_STRING_FEMALE

    return GENDER_STRING_UNSURE
