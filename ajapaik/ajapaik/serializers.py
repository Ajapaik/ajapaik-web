import logging

from django.db.models import Count, Q, Case, When, Value, BooleanField, \
    IntegerField
from django.urls import reverse
from django.utils import timezone
from rest_framework import serializers

from ajapaik.utils import calculate_thumbnail_size
from .models import Album, Dating, Profile, Video, Photo, _get_pseudo_slug_for_photo

log = logging.getLogger(__name__)


class AlbumDetailsSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='name')
    image = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()

    def get_image(self, instance):
        request = self.context['request']
        return request.build_absolute_uri(
            reverse('api_album_thumb', args=(instance.id,))
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


class AlbumSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='name')
    photos = serializers.SerializerMethodField()

    def get_photos(self, instance):
        request = self.context['request']
        user_profile = request.user.profile if request.user.is_authenticated else None

        photos = PhotoSerializer.annotate_photos(
            self.context['photos'],
            user_profile
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


class CuratorAlbumInfoSerializer(serializers.ModelSerializer):
    parent_album_id = serializers.SerializerMethodField()
    parent_album_name = serializers.SerializerMethodField()

    def get_parent_album_id(self, obj: Album):
        return obj.subalbum_of.id if obj.subalbum_of else None

    def get_parent_album_name(self, obj: Album):
        return obj.subalbum_of.name if obj.subalbum_of else None

    class Meta:
        model = Album
        fields = ('id', 'name', 'description', 'open', 'is_public', 'parent_album_id', 'parent_album_name')


class CuratorAlbumSelectionAlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ('id', 'name', 'open')


class CuratorMyAlbumListAlbumSerializer(serializers.ModelSerializer):
    photo_count = serializers.IntegerField(source='photos.count')

    class Meta:
        model = Album
        fields = ('id', 'name', 'photo_count')


class DatingSerializer(serializers.ModelSerializer):
    profile_id = serializers.IntegerField(source='profile.id', required=False)
    full_name = serializers.CharField(source='profile.get_display_name', required=False)
    confirmation_count = serializers.IntegerField(source='confirmations.count')
    this_user_has_confirmed = serializers.BooleanField()

    class Meta:
        model = Dating
        fields = ('id', 'profile_id', 'comment', 'full_name', 'confirmation_count', 'raw', 'this_user_has_confirmed')


class DateTimeTzAwareField(serializers.DateTimeField):
    def to_representation(self, value):
        value = timezone.localtime(value)
        return super(DateTimeTzAwareField, self).to_representation(value)


class FrontpageAlbumSerializer(serializers.ModelSerializer):
    # TODO: Think about what to do about the search thing
    cover_photo_height = serializers.IntegerField()
    cover_photo_width = serializers.IntegerField()
    album_type = serializers.SerializerMethodField('get_album_type')

    class Meta:
        model = Album
        fields = ('id', 'name', 'cover_photo_height', 'cover_photo_width', 'cover_photo_flipped',
                  'photo_count_with_subalbums', 'cover_photo', 'geotagged_photo_count_with_subalbums',
                  'comments_count_with_subalbums', 'rephoto_count_with_subalbums', 'is_film_still_album',
                  'album_type')

    def get_album_type(self, instance):
        return instance.get_album_type


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
            'image_thumb',
            args=(instance.id, 400, _get_pseudo_slug_for_photo(instance.get_display_text, None, instance.id))
        )

    def get_permalink(self, instance):
        return reverse(
            'photo',
            args=(instance.id, _get_pseudo_slug_for_photo(instance.get_display_text, None, instance.id))
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
    full_image = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField('get_display_text')
    date = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()
    longitude = serializers.FloatField(source='lon')
    latitude = serializers.FloatField(source='lat')
    azimuth = serializers.FloatField()
    rephotos = serializers.SerializerMethodField()
    favorited = serializers.BooleanField()

    @classmethod
    def annotate_photos(cls, photos_queryset, user_profile):
        '''
        Helper function to annotate photo with special fields required by this
        serializer.
        Adds "rephotos_count", "uploads_count", "favorited". Field "likes_count"
        added to determine is photo liked(favorited) by user.
        '''
        # There is bug in Django about irrelevant selection returned when
        # annotating on multiple tables. https://code.djangoproject.com/ticket/10060
        # So if faced some incorrect data check what have been assigned to
        # "instance" variable.
        return photos_queryset \
            .prefetch_related('source') \
            .prefetch_related('rephotos') \
            .annotate(rephotos_count=Count('rephotos')) \
            .annotate(uploads_count=Count(Case(When(rephotos__user=user_profile, then=1),
                                               output_field=IntegerField()))) \
            .annotate(likes_count=Count('likes')) \
            .annotate(favorited=Case(When(Q(likes__profile=user_profile) & Q(likes__profile__isnull=False),
                                          then=Value(True)), default=Value(False), output_field=BooleanField()))

    def get_display_text(self, instance: Photo):
        return instance.get_display_text

    def get_full_image(self, instance: Photo):
        request = self.context['request']
        image_name = str(instance.image)
        prefix = 'uploads/'

        if image_name.startswith(prefix):
            image_name = image_name[len(prefix):]

        iiif_jpeg = request.build_absolute_uri(f'/iiif/work/iiif/ajapaik/{image_name}.tif/full/max/0/default.jpg')
        return iiif_jpeg

    def get_image(self, instance: Photo):
        request = self.context['request']
        relative_url = reverse('image_thumb', args=(instance.id,))

        return '{}[DIM]/'.format(request.build_absolute_uri(relative_url))

    def get_date(self, instance):
        if instance.date:
            return instance.date.strftime('%d-%m-%Y')
        else:
            return instance.date_text

    def get_source(self, instance: Photo):
        if instance.source:
            source_key = instance.source_key or ''
            return {
                'url': instance.source_url,
                'name': f'{instance.source.description} {source_key}'.strip(),
            }
        else:
            return {
                'url': instance.source_url,
            }

    def get_rephotos(self, instance: Photo):
        return RephotoSerializer(
            instance=instance.rephotos.all(),
            many=True,
            context={'request': self.context['request']},
        ).data

    class Meta:
        model = Photo
        fields = (
            'id', 'image', 'full_image', 'width', 'height', 'title', 'date',
            'author', 'source', 'latitude', 'longitude', 'azimuth', 'rephotos',
            'favorited',
        )


class PhotoWithDistanceSerializer(PhotoSerializer):
    distance = serializers.IntegerField(source='distance.m', read_only=True)

    class Meta(PhotoSerializer.Meta):
        fields = (
            'id', 'distance', 'image', 'width', 'height', 'title', 'date',
            'author', 'source', 'latitude', 'longitude', 'azimuth', 'rephotos',
            'favorited',
        )


class ProfileLinkSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='get_display_name')
    profile_url = serializers.CharField(source='get_profile_url')

    class Meta:
        model = Profile
        fields = (
            'name', 'profile_url'
        )


class RephotoSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    date = DateTimeTzAwareField(format='%d-%m-%Y')
    source = serializers.SerializerMethodField()
    user_name = serializers.CharField(source='user.user.get_full_name', default='Anonymous user')
    is_uploaded_by_current_user = serializers.SerializerMethodField()

    def get_image(self, instance):
        request = self.context['request']
        relative_url = reverse('image_thumb', args=(instance.id,))
        return '{}[DIM]/'.format(request.build_absolute_uri(relative_url))

    def get_date(self, instance: Photo):
        if instance.date:
            return instance.date.strftime('%d-%m-%Y')
        else:
            return instance.date_text

    def get_source(self, instance: Photo):
        if instance.source:
            source_key = instance.source_key or ''
            return {
                'url': instance.source_url,
                'name': f'{instance.source.description} {source_key}'.strip(),
            }
        else:
            return {
                'url': instance.source_url,
            }

    def get_is_uploaded_by_current_user(self, instance):
        user = self.context['request'].user
        if user.is_authenticated:
            return instance.user == self.context['request'].user.profile
        else:
            return False

    class Meta:
        model = Photo
        fields = (
            'image', 'date', 'source', 'user_name',
            'is_uploaded_by_current_user',
        )


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        exclude = ('created', 'modified')
