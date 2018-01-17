import logging

from django.core.urlresolvers import reverse
from django.db.models import Count, Q, Case, When, Value, BooleanField, \
    IntegerField
from rest_framework import serializers

from .models import Album, Dating, Video, Photo, _get_pseudo_slug_for_photo
from project.utils import calculate_thumbnail_size


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


class PhotoSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()
    longitude = serializers.FloatField(source='lon')
    latitude = serializers.FloatField(source='lat')
    rephotos = serializers.IntegerField(source='rephotos_count')
    uploads = serializers.IntegerField(source='uploads_count')
    favorited = serializers.BooleanField()

    def get_image(self, instance):
        request = self.context.get('request')
        if request is None:
            log.warning('%s require request instance to generate absolute '
                        'image thumbnail path.', self.__class__.__name__)
            return
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

    class Meta:
        model = Photo
        fields = (
            'id', 'image', 'width', 'height', 'title', 'date',
            'author', 'source', 'latitude', 'longitude', 'rephotos', 'uploads',
            'favorited',
        )


class PhotoWithDistanceSerializer(PhotoSerializer):
    distance = serializers.IntegerField(source='distance.m', read_only=True)

    class Meta(PhotoSerializer.Meta):
        fields = (
            'id', 'distance', 'image', 'width', 'height', 'title', 'date',
            'author', 'source', 'latitude', 'longitude', 'rephotos', 'uploads',
            'favorited',
        )


class AlbumDetailsSerializer(serializers.Serializer):
    photos = serializers.SerializerMethodField()

    def get_photos(self, instance):
        request = self.context.get('request')
        if request is None:
            log.warning('%s require HTTP request for proper functioning of %s',
                        self.__class__.__name__,
                        PhotoSerializer.__class__.__name__)
            return {}

        user_profile = request.user.profile
        # There is bug in Django about irrelevant selection returned when
        # annotating on multiple tables. https://code.djangoproject.com/ticket/10060
        # So if faced some incorect data check what have been assigned to
        # photos variable.
        photos = Photo.objects.filter(
            Q(albums=instance)
            | (Q(albums__subalbum_of=instance) & ~Q(albums__atype=Album.AUTO)),
            rephoto_of__isnull=True
        ) \
            .prefetch_related('source') \
            .annotate(rephotos_count=Count('rephotos')) \
            .annotate(uploads_count=Count(
                Case(
                    When(rephotos__user=user_profile, then=1),
                    output_field=IntegerField()
                )
            ),) \
            .annotate(likes_count=Count('likes')) \
            .annotate(favorited=Case(
                When(likes_count__gt=0, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()))
        return PhotoSerializer(instance=photos,
                               many=True,
                               context={'request': request}).data

    class Meta(object):
        model = Album
        fields = ('title', 'photos')
