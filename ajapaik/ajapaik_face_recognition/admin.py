from django.contrib import admin
from ajapaik.ajapaik.autocomplete import autocomplete_form_factory

from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle, FaceRecognitionRectangleFeedback, \
    FaceRecognitionUserGuess


class FaceRecognitionRectangleAdmin(admin.ModelAdmin):
    form = autocomplete_form_factory(FaceRecognitionRectangle)


class FaceRecognitionRectangleFeedbackAdmin(admin.ModelAdmin):
    form = autocomplete_form_factory(FaceRecognitionRectangleFeedback)


class FaceRecognitionUserGuessAdmin(admin.ModelAdmin):
    form = autocomplete_form_factory(FaceRecognitionUserGuess)


admin.site.register(FaceRecognitionRectangle, FaceRecognitionRectangleAdmin)
admin.site.register(FaceRecognitionRectangleFeedback, FaceRecognitionRectangleFeedbackAdmin)
admin.site.register(FaceRecognitionUserGuess, FaceRecognitionUserGuessAdmin)
