from django.http import QueryDict

from ajapaik.ajapaik_object_recognition.object_annotation_utils import parse_parameter


class AddDetectionAnnotation:
    def __init__(self, parameters: QueryDict, user_id: int):
        self.object_id = parse_parameter(parameters['objectId'])
        self.subject_id = parse_parameter(parameters['subjectId'])

        self.photo_id = parameters['photoId']

        self.x1 = parameters['x1']
        self.x2 = parameters['x2']
        self.y1 = parameters['y1']
        self.y2 = parameters['y2']

        self.user_id = user_id
