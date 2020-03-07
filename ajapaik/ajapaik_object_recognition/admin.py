from django.contrib import admin
from . import models

admin.site.register(models.ObjectAnnotationClass)
admin.site.register(models.ObjectDetectionModel)
admin.site.register(models.ObjectDetectionAnnotation)
admin.site.register(models.ObjectAnnotationFeedback)
