from models import Photo, Area, Source, Album
from rest_framework import serializers


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('id', 'image', 'date_text', 'description', 'source_key', 'source_url', 'source', 'city', 'lat', 'lon',
                  'azimuth', 'confidence', 'azimuth_confidence')


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ('id', 'name', 'lat', 'lon')


class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ('id', 'name', 'lat', 'lon')


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ('id', 'name', 'description')