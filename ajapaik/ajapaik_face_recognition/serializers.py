from rest_framework import serializers

from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle


class FaceRecognitionRectangleSerializer(serializers.ModelSerializer):
    coordinates = serializers.ReadOnlyField(source='decode_coordinates')

    class Meta:
        model = FaceRecognitionRectangle
        fields = ('id', 'coordinates',)
