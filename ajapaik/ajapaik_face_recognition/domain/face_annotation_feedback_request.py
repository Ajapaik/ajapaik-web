from django.http import QueryDict

from ajapaik.ajapaik_object_recognition import object_annotation_utils


class FaceAnnotationFeedbackRequest:
    def __init__(self, user_id: int, annotation_id: int, parameters: QueryDict):
        self.user_id = user_id
        self.annotation_id = annotation_id

        self.is_confirmation = object_annotation_utils.parse_boolean(parameters['isFaceAnnotation'])
        self.is_correct_name = object_annotation_utils.parse_boolean(parameters['isCorrectName'])
        self.alternative_subject_id = object_annotation_utils.parse_parameter(parameters['alternativeSubjectId'])
