from django.http import QueryDict

from ajapaik.ajapaik_object_recognition import object_annotation_utils
from ajapaik.ajapaik_object_recognition.object_annotation_utils import parse_age_parameter, parse_gender_parameter


class FaceAnnotationUpdateRequest:
    def __init__(self, parameters: QueryDict, annotation_id: int, user_id: int):
        self.annotation_id = annotation_id

        self.new_subject_id = object_annotation_utils.parse_parameter(parameters['newSubjectId'])
        self.new_age_guess = parse_age_parameter(parameters['ageGroup'])
        self.new_gender_guess = parse_gender_parameter(parameters['gender'])

        self.user_id = user_id
