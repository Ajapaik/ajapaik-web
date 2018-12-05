import autocomplete_light
from django.contrib import admin

from project.ajapaik_face_recognition.models import FaceRecognitionRectangle, FaceRecognitionRectangleFeedback, \
    FaceRecognitionSubject, FaceRecognitionUserGuess


class FaceRecognitionRectangleAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(FaceRecognitionRectangle, fields='__all__')


class FaceRecognitionRectangleFeedbackAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(FaceRecognitionRectangleFeedback, fields='__all__')


class FaceRecognitionSubjectAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(FaceRecognitionSubject, fields='__all__')


class FaceRecognitionUserGuessAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(FaceRecognitionUserGuess, fields='__all__')


admin.site.register(FaceRecognitionRectangle, FaceRecognitionRectangleAdmin)
admin.site.register(FaceRecognitionRectangleFeedback, FaceRecognitionRectangleFeedbackAdmin)
admin.site.register(FaceRecognitionSubject, FaceRecognitionSubjectAdmin)
admin.site.register(FaceRecognitionUserGuess, FaceRecognitionUserGuessAdmin)
