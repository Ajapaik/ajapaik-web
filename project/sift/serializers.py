from models import CatPhoto, CatTag
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