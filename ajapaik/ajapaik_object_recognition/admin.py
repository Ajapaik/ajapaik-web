from django.contrib import admin
from . import models

admin.site.register(models.DetectionClass)
admin.site.register(models.DetectionModel)
admin.site.register(models.ObjectDetectionRectangle)
admin.site.register(models.ObjectDetectionFeedback)
