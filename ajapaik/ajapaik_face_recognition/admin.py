import autocomplete_light
from django.contrib import admin

from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle, FaceRecognitionRectangleFeedback, \
    FaceRecognitionUserGuess


class FaceRecognitionRectangleAdmin(admin.ModelAdmin):
    form = autocomplete_light.shortcuts.modelform_factory(FaceRecognitionRectangle, fields='__all__')


class FaceRecognitionRectangleFeedbackAdmin(admin.ModelAdmin):
    form = autocomplete_light.shortcuts.modelform_factory(FaceRecognitionRectangleFeedback, fields='__all__')


class FaceRecognitionUserGuessAdmin(admin.ModelAdmin):
    form = autocomplete_light.shortcuts.modelform_factory(FaceRecognitionUserGuess, fields='__all__')


admin.site.register(FaceRecognitionRectangle, FaceRecognitionRectangleAdmin)
admin.site.register(FaceRecognitionRectangleFeedback, FaceRecognitionRectangleFeedbackAdmin)
admin.site.register(FaceRecognitionUserGuess, FaceRecognitionUserGuessAdmin)
