from django.db import models
from ajapaik.ajapaik.models import Photo, Profile


class ObjectDetectionModel(models.Model):
    model_file_name = models.TextField(max_length=200)

    def __str__(self):
        return self.model_file_name


class ObjectAnnotationClass(models.Model):
    alias = models.TextField(max_length=200, null=True)
    wiki_data_id = models.TextField(max_length=30)
    translations = models.TextField()
    detection_model = models.ForeignKey(ObjectDetectionModel)

    def __str__(self):
        return self.label


class ObjectDetectionAnnotation(models.Model):
    x1 = models.FloatField()
    x2 = models.FloatField()
    y1 = models.FloatField()
    y2 = models.FloatField()

    photo = models.ForeignKey(Photo)
    detected_object = models.ForeignKey(ObjectAnnotationClass)

    user = models.ForeignKey(Profile)

    is_manual_detection = models.BooleanField()

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    deleted_on = models.DateTimeField(null=True)

    def __str__(self):
        return f'Detected {self.detected_object.__str__()} on photo {self.photo.id} at ' \
            f'x1: {self.x1}, y1: {self.y1}, x2: {self.x2}, y2: {self.y2}'


class ObjectAnnotationFeedback(models.Model):
    object_detection_annotation = models.ForeignKey(ObjectDetectionAnnotation, related_name="feedback")

    confirmation = models.BooleanField(default=True)
    alternative_object = models.ForeignKey(ObjectAnnotationClass, null=True)

    user = models.ForeignKey(Profile)

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        string_label = ''

        if self.confirmation:
            string_label += f'Confirmed annotation {self.object_detection_annotation.id}'
        else:
            string_label += f'Rejected annotation {self.object_detection_annotation.id}'

        if self.alternative_object is not None:
            string_label += f', alternative object suggested: {self.alternative_object.__str__()}'

        return string_label
