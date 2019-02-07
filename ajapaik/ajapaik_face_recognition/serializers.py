from rest_framework import serializers

from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle


class FaceRecognitionRectangleSerializer(serializers.ModelSerializer):
    coordinates = serializers.ReadOnlyField(source='decode_coordinates')
    subject_name = serializers.ReadOnlyField(source='get_subject_name')

    class Meta:
        model = FaceRecognitionRectangle
        fields = ('id', 'coordinates', 'subject_name')
