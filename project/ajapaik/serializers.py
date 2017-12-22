from rest_framework import serializers

from models import Album, Dating, Video, Photo


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


class FrontpageAlbumSerializer(serializers.ModelSerializer):
    cover_photo_height = serializers.IntegerField()
    cover_photo_width = serializers.IntegerField()

    class Meta:
        model = Album
        fields = ('id', 'name', 'cover_photo_height', 'cover_photo_width', 'cover_photo_flipped',
                  'photo_count_with_subalbums', 'cover_photo', 'geotagged_photo_count_with_subalbums',
                  'comments_count_with_subalbums', 'rephoto_count_with_subalbums', 'is_film_still_album')


class DatingSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='profile.get_display_name')
    confirmation_count = serializers.IntegerField(source='confirmations.count')
    this_user_has_confirmed = serializers.BooleanField()

    class Meta:
        model = Dating
        fields = ('id', 'comment', 'full_name', 'confirmation_count', 'raw', 'this_user_has_confirmed')


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        exclude = ('created', 'modified')


class BasePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('id', )


class PhotoGeodataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('lat', 'lon')


class PhotoMapMarkerSerializer(BasePhotoSerializer, PhotoGeodataSerializer):
    rephoto_count = serializers.IntegerField()
    class Meta:
        model = Photo
        fields = ('id', 'lat', 'lon', 'azimuth', 'rephoto_count')
