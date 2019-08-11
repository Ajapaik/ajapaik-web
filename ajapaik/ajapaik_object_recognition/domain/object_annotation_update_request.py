from django.http import QueryDict


class ObjectAnnotationUpdateRequest:
    def __init__(self, parameters: QueryDict):
        self.rectangle_id = parameters['rectangleId']
        self.alternative_object_id = parameters['objectId']
