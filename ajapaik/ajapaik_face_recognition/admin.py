from django.contrib import admin
from ajapaik.ajapaik.autocomplete import autocomplete_form_factory

from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle, FaceRecognitionRectangleFeedback, \
    FaceRecognitionUserSuggestion


class FaceRecognitionRectangleAdmin(admin.ModelAdmin):
    form = autocomplete_form_factory(FaceRecognitionRectangle)


class FaceRecognitionRectangleFeedbackAdmin(admin.ModelAdmin):
    form = autocomplete_form_factory(FaceRecognitionRectangleFeedback)


class FaceRecognitionUserSuggestionAdmin(admin.ModelAdmin):
    form = autocomplete_form_factory(FaceRecognitionUserSuggestion)


admin.site.register(FaceRecognitionRectangle, FaceRecognitionRectangleAdmin)
admin.site.register(FaceRecognitionRectangleFeedback, FaceRecognitionRectangleFeedbackAdmin)
admin.site.register(FaceRecognitionUserSuggestion, FaceRecognitionUserSuggestionAdmin)
