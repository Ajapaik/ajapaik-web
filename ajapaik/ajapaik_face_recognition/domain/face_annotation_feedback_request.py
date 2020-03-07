from django.http import QueryDict

from ajapaik.ajapaik_object_recognition import object_annotation_utils
from ajapaik.ajapaik_object_recognition.object_annotation_utils import parse_age_parameter, parse_gender_parameter


class FaceAnnotationFeedbackRequest:
    def __init__(self, user_id: int, annotation_id: int, parameters: QueryDict):
        self.user_id = user_id
        self.annotation_id = annotation_id

        self.is_confirmation = object_annotation_utils.parse_boolean(parameters['isFaceAnnotation'])
        self.is_correct_name = object_annotation_utils.parse_boolean(parameters['isCorrectName'])
        self.alternative_subject_id = object_annotation_utils.parse_parameter(parameters['alternativeSubjectId'])

        self.is_correct_age = object_annotation_utils.parse_boolean(parameters['isCorrectAge'])
        self.alternative_age = parse_age_parameter(parameters['alternativeAgeGroup'])

        self.is_correct_gender = object_annotation_utils.parse_boolean(parameters['isCorrectGender'])
        self.alternative_gender = parse_gender_parameter(parameters['alternativeGender'])
