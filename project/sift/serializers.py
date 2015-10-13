from models import CatPhoto, CatTag, CatAlbum
from rest_framework import serializers


class CatResultsPhotoSerializer(serializers.ModelSerializer):
    thumb_height = serializers.IntegerField()
    thumb_width = serializers.IntegerField()

    class Meta:
        model = CatPhoto
        fields = ('id', 'title', 'thumb_height', 'thumb_width', 'source_url')


class CatTaggerTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatTag
        fields = ('name',)


class CatCuratorAlbumSelectionAlbumSerializer(serializers.ModelSerializer):
    photo_count = serializers.IntegerField(source='photos.count')

    class Meta:
        model = CatAlbum
        fields = ('id', 'title', 'subtitle', 'photo_count')