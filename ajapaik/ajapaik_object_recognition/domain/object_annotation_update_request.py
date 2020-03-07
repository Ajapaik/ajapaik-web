from django.http import QueryDict


class ObjectAnnotationUpdateRequest:
    def __init__(self, parameters: QueryDict):
        self.rectangle_id = parameters['rectangleId']
        self.wiki_data_label_id = parameters['wikiDataLabelId']
