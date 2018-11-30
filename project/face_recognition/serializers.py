from rest_framework import serializers

from project.face_recognition.models import FaceRecognitionRectangle


class FaceRecognitionRectangleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceRecognitionRectangle
        fields = ('id', 'coordinates',)
