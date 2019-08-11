import json
from django.http import QueryDict
from django.utils import timezone


DELETION_EXPIRATION_THRESHOLD_IN_HOURS = 24


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
