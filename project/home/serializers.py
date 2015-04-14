from django.core.urlresolvers import reverse
from models import Photo, Area, Source, Album, CatAlbum
from rest_framework import serializers


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('id', 'image', 'date_text', 'title', 'description', 'source_key', 'source_url', 'source', 'area', 'lat', 'lon',
                  'azimuth', 'confidence', 'azimuth_confidence')


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ('id', 'name', 'lat', 'lon')


class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ('id', 'name')


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


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ('id', 'name', 'description')


class FrontpageHistoricInfiniteScrollSerializer(serializers.ModelSerializer):
    thumb = serializers.SerializerMethodField('get_frontpage_thumb')

    def get_frontpage_thumb(self, instance):
        return reverse('project.home.views.photo_thumb', args=(instance.id, 300)),

    class Meta:
        model = Photo
        fields = ('id', 'description', 'thumb')


class FrontpageRephotoInfiniteScrollSerializer(serializers.ModelSerializer):
    original = serializers.SerializerMethodField('get_original_thumb')
    rephoto = serializers.SerializerMethodField('get_rephoto_thumb')

    def get_original_thumb(self, instance):
        return reverse('project.home.views.photo_thumb', args=(instance.rephoto_of_id, 300)),

    def get_rephoto_thumb(self, instance):
        return reverse('project.home.views.photo_thumb', args=(instance.id, 300)),

    class Meta:
        model = Photo
        fields = ('id', 'description', 'original', 'rephoto')