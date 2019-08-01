from django.db import models
from ajapaik.ajapaik.models import Photo, Profile


class DetectionModel(models.Model):
    model_file_name = models.TextField(max_length=200)

    def __str__(self):
        return self.model_file_name


class DetectionClass(models.Model):
    label = models.TextField(max_length=200)
    detection_model = models.ForeignKey(DetectionModel)

    def __str__(self):
        return self.label


class ObjectDetectionRectangle(models.Model):
    x1 = models.FloatField()
    x2 = models.FloatField()
    y1 = models.FloatField()
    y2 = models.FloatField()

    photo = models.ForeignKey(Photo)
    detected_object = models.ForeignKey(DetectionClass)

    user = models.ForeignKey(Profile)

    is_manual_detection = models.BooleanField()

    created_on = models.DateTimeField()
    modified_on = models.DateTimeField()
    deleted_on = models.DateTimeField(null=True)

    def __str__(self):
        return f'Detected {self.detected_object.label} on photo {self.photo.id} at ' \
            f'x1: {self.x1}, y1: {self.y1}, x2: {self.x2}, y2: {self.y2}'


class ObjectDetectionFeedback(models.Model):
    object_detection_rectangle = models.ForeignKey(ObjectDetectionRectangle)

    confirmation = models.BooleanField(default=True)

    user = models.ForeignKey(Profile)

    def __str__(self):
        return f'For rectangle {self.objectDetectionRectangle.id}: ' \
            f'confirmations {self.confirmations}, rejections {self.rejections}'
