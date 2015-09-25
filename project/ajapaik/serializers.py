from models import Album, Photo
from rest_framework import serializers


class CuratorAlbumSelectionAlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ('id', 'name', 'open')


class CuratorMyAlbumListAlbumSerializer(serializers.ModelSerializer):
    photo_count = serializers.IntegerField(source='photos.count')

    class Meta:
        model = Album
        fields = ('id', 'name', 'photo_count')


class CuratorAlbumInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ('id', 'name', 'description', 'open', 'is_public', 'subalbum_of')


class DelfiBboxResponseSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        pass

    def to_representation(self, value):
        pass

    def to_internal_value(self, data):
        pass

    def update(self, instance, validated_data):
        pass

    class Meta:
        model = Photo
        fields = ('lat', 'lon', 'thumbURL', 'URL', 'description')