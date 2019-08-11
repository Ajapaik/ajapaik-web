from django.http import QueryDict

from ajapaik.ajapaik_object_recognition import object_annotation_utils


class AddObjectDetectionFeedback:
    def __init__(self, parameters: QueryDict, user_id: int, annotation_id: int):
        self.user_id = user_id

        self.object_annotation_id = object_annotation_utils.parse_parameter(annotation_id)
        self.is_confirmation = parameters['isConfirmed'] in ['True', 'true']
        self.alternative_object_id = object_annotation_utils.parse_parameter(parameters['alternativeObjectId'])
