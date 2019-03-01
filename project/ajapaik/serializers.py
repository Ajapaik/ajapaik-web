import logging

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.db.models import BooleanField, Case, Count, Value, When
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from project.utils import calculate_thumbnail_size

from .models import (Album, Dating, Licence, Photo, Video,
                     _get_pseudo_slug_for_photo)

log = logging.getLogger(__name__)


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
        fields = (
            'id', 'name', 'description', 'open', 'is_public', 'subalbum_of'
        )


class FrontpageAlbumSerializer(serializers.ModelSerializer):
    cover_photo_height = serializers.IntegerField()
    cover_photo_width = serializers.IntegerField()

    class Meta:
        model = Album
        fields = (
            'id', 'name', 'cover_photo_height', 'cover_photo_width',
            'cover_photo_flipped', 'photo_count_with_subalbums', 'cover_photo',
            'geotagged_photo_count_with_subalbums',
            'comments_count_with_subalbums', 'rephoto_count_with_subalbums',
            'is_film_still_album'
        )


class DatingSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='profile.get_display_name')
    confirmation_count = serializers.IntegerField(source='confirmations.count')
    this_user_has_confirmed = serializers.BooleanField()

    class Meta:
        model = Dating
        fields = (
            'id', 'comment', 'full_name', 'confirmation_count', 'raw',
            'this_user_has_confirmed'
        )


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        exclude = ('created', 'modified')


class PhotoMapMarkerSerializer(serializers.ModelSerializer):
    rephoto_count = serializers.IntegerField()

    url = serializers.SerializerMethodField()
    permalink = serializers.SerializerMethodField()
    width = serializers.SerializerMethodField()
    height = serializers.SerializerMethodField()
    is_selected = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        self.photo_selection = []
        if 'photo_selection' in kwargs:
            self.photo_selection = kwargs['photo_selection']
            # Django REST framework don't happy with unexpected parameters.
            del kwargs['photo_selection']
        super(PhotoMapMarkerSerializer, self).__init__(*args, **kwargs)

    def get_url(self, instance):
        return reverse(
            'project.ajapaik.views.image_thumb',
            args=(
                instance.id,
                400,
                _get_pseudo_slug_for_photo(instance.description, None, None)
            )
        )

    def get_permalink(self, instance):
        return reverse(
            'project.ajapaik.views.photoslug',
            args=(
                instance.id,
                _get_pseudo_slug_for_photo(instance.description, None, None)
            )
        )

    def get_width(self, instance):
        return calculate_thumbnail_size(instance.width, instance.height, 400)[0]

    def get_height(self, instance):
        return calculate_thumbnail_size(instance.width, instance.height, 400)[1]

    def get_is_selected(self, instance):
        return str(instance.id) in self.photo_selection

    class Meta:
        model = Photo
        fields = (
            'id', 'lat', 'lon', 'azimuth', 'rephoto_count', 'description',
            'comment_count', 'url', 'permalink', 'width', 'height',
            'is_selected'
        )


class RephotoSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()
    user_name = serializers.CharField(source='user.user.get_full_name')
    is_uploaded_by_current_user = serializers.SerializerMethodField()

    def get_image(self, instance):
        request = self.context['request']
        relative_url = reverse(
            "project.ajapaik.views.image_thumb", args=(instance.id,)
        )
        return '{}[DIM]/'.format(request.build_absolute_uri(relative_url))

    def get_date(self, instance):
        if instance.date:
            return instance.date.strftime('%d-%m-%Y')
        else:
            return instance.date_text

    def get_source(self, instance):
        if instance.source:
            return {
                'url': instance.source_url,
                'name': instance.source.description + ' ' + instance.source_key,
            }
        else:
            return {
                'url': instance.source_url,
            }

    def get_is_uploaded_by_current_user(self, instance):
        user = self.context['request'].user
        if user is None:
            return False
        return instance.user == user.profile

    class Meta:
        model = Photo
        fields = (
            'image', 'date', 'source', 'user_name',
            'is_uploaded_by_current_user',
        )


class PhotoSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    title = serializers.CharField(source='description')
    date = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()
    longitude = serializers.FloatField(source='lon')
    latitude = serializers.FloatField(source='lat')
    azimuth = serializers.FloatField()
    rephotos = serializers.SerializerMethodField()
    favorited = serializers.SerializerMethodField()

    @classmethod
    def annotate_photos(cls, photos_queryset, user_profile=None):
        '''
        Helper function to annotate photo with special fields required by this
        serializer.
        '''
        # There is bug in Django about irrelevant selection returned when
        # annotating on multiple tables. Check next link for more details:
        # https://code.djangoproject.com/ticket/10060
        # So if faced some incorect data check what have been assigned to
        # "photos_queryset" variable.
        photos_queryset = photos_queryset \
            .prefetch_related('source') \
            .prefetch_related('rephotos')
        if user_profile is not None:
            # Determine is photo like by current user.
            photos_queryset = photos_queryset \
                .annotate(
                    favorited=Case(
                        When(likes__profile=user_profile,
                             then=Value(True)),
                        default=Value(False),
                        output_field=BooleanField())
                )
        return photos_queryset

    def get_image(self, instance):
        request = self.context['request']
        relative_url = reverse(
            "project.ajapaik.views.image_thumb", args=(instance.id,)
        )
        return '{}[DIM]/'.format(request.build_absolute_uri(relative_url))

    def get_date(self, instance):
        if instance.date:
            return instance.date.strftime('%d-%m-%Y')
        else:
            return instance.date_text

    def get_source(self, instance):
        if instance.source:
            return {
                'url': instance.source_url,
                'name': instance.source.description + ' ' + instance.source_key,
            }
        else:
            return {
                'url': instance.source_url,
            }

    def get_rephotos(self, instance):
        return RephotoSerializer(
            instance=instance.rephotos.all(),
            many=True,
            context={'request': self.context['request']},
        ).data

    def get_favorited(self, instance):
        return getattr(instance, 'favorited', False)

    class Meta:
        model = Photo
        fields = (
            'id', 'image', 'width', 'height', 'title', 'date', 'author',
            'source', 'latitude', 'longitude', 'azimuth', 'rephotos',
            'favorited',
        )


class PhotoWithDistanceSerializer(PhotoSerializer):
    distance = serializers.IntegerField(source='distance.m', read_only=True)

    class Meta(PhotoSerializer.Meta):
        fields = (
            'id', 'distance', 'image', 'width', 'height', 'title', 'date',
            'author', 'source', 'latitude', 'longitude', 'rephotos',
            'favorited',
        )


class AlbumSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='name')
    photos = serializers.SerializerMethodField()

    def get_photos(self, instance):
        request = self.context['request']
        photos = PhotoSerializer.annotate_photos(
            self.context['photos'],
            request.user and request.user.profile
        )
        return PhotoSerializer(
            instance=photos,
            many=True,
            context={
                'request': request
            }
        ).data

    class Meta(object):
        model = Album
        fields = ('title', 'photos')


class AlbumDetailsSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='name')
    image = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()

    def get_image(self, instance):
        request = self.context['request']
        return request.build_absolute_uri(
            reverse('project.ajapaik.api.api_album_thumb', args=(instance.id,))
        )

    def get_stats(self, instance):
        return {
            'rephotos': instance.rephotos_count,
            # Currently rephotos don't belong to original photo album.
            'total': instance.photos_count + instance.rephotos_count
        }

    @classmethod
    def annotate_albums(cls, albums_queryset):
        return albums_queryset \
            .annotate(rephotos_count=Count('photos__rephotos')) \
            .annotate(photos_count=Count('photos'))

    class Meta(object):
        model = Album
        fields = ('id', 'title', 'image', 'stats')


class UserProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    authentication_token = serializers.SerializerMethodField()

    def get_authentication_token(self, instance):
        token, status = Token.objects.get_or_create(user=instance)
        return token.key

    class Meta(object):
        model = get_user_model()
        fields = ('id', 'authentication_token')


class LicenceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    url = serializers.CharField()
    image_url = serializers.CharField()
    is_public = serializers.BooleanField()

    class Meta(object):
        model = Licence
        fields = ('id', 'name', 'url', 'image_url', 'is_public')
