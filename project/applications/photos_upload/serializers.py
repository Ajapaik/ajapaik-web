"""
Mass upload Serializers.
"""
from rest_framework import serializers

from project.ajapaik.models import Photo, Licence, Album


class PhotoSerializer(serializers.Serializer):
    """
    Serializer for photos creation and serialization for massive upload form.
    """
    name = serializers.CharField(source='title')
    description = serializers.CharField()
    longitude = serializers.FloatField(source='lon')
    latitude = serializers.FloatField(source='lat')
    azimuth = serializers.FloatField()
    isUserAuthor = serializers.BooleanField()
    licence = serializers.PrimaryKeyRelatedField(queryset=Licence.objects.all())
    albums = serializers.PrimaryKeyRelatedField(
        queryset=Album.objects.filter(is_public=True),
        many=True
    )

    class Meta:
        fields = [
            'name', 'description', 'longitude', 'latitude', 'azimuth',
            'is_user_author', 'licence', 'albums'
        ]
