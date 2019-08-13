from django.http import QueryDict

from ajapaik.ajapaik_object_recognition import object_annotation_utils


class FaceAnnotationUpdateRequest:
    def __init__(self, parameters: QueryDict, annotation_id: int):
        self.annotation_id = annotation_id
        self.new_subject_id = object_annotation_utils.parse_parameter(parameters['newSubjectId'])
