import logging

from django.contrib.sites.models import Site
from django.db.models import Count
from django.urls import reverse
from django.utils import timezone
from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from .models import Album, Dating, Video, Photo, ImageSimilarity, Source, Licence
from .types import GalleryResults

log = logging.getLogger(__name__)


def get_base_uri(obj) -> str:
    'https://%s%s' % (Site.objects.get_current().domain, obj.get_absolute_url())


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


class PhotoMiniSerializer(serializers.ModelSerializer):
    slug = serializers.SerializerMethodField()

    def get_slug(self, instance: Photo) -> str:
        return instance.get_pseudo_slug

    class Meta(object):
        model = Photo
        fields = ['id', 'slug']


class PhotoFaceCategorizationSerializer(PhotoMiniSerializer):
    class Meta(PhotoMiniSerializer.Meta):
        model = Photo
        fields = [*PhotoMiniSerializer.Meta.fields, 'width', 'height']


class PhotoRepresentationSerializer(PhotoMiniSerializer):
    display_text = serializers.SerializerMethodField('get_display_text')

    def get_display_text(self, instance: Photo):
        return instance.get_display_text

    class Meta(PhotoMiniSerializer.Meta):
        model = Photo
        fields = [*PhotoMiniSerializer.Meta.fields, 'title', 'display_text']


class AlbumMiniSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Album
        fields = ['name']


class AlbumPreviewSerializer(AlbumMiniSerializer):
    class Meta(AlbumMiniSerializer.Meta):
        model = Album
        fields = ["id", *AlbumMiniSerializer.Meta.fields]


class GalleryAlbumSerializer(AlbumPreviewSerializer):
    class Meta(AlbumPreviewSerializer.Meta):
        model = Album
        fields = [*AlbumPreviewSerializer.Meta.fields, "lat", "lon"]


class CuratorAlbumInfoSerializer(serializers.ModelSerializer):
    parent_album_id = serializers.SerializerMethodField()
    parent_album_name = serializers.SerializerMethodField()

    def get_parent_album_id(self, obj):
        return obj.subalbum_of.id if obj.subalbum_of else None

    def get_parent_album_name(self, obj):
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
    cover_photo_height = serializers.IntegerField()
    cover_photo_width = serializers.IntegerField()
    album_type = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = ('id', 'name', 'cover_photo_height', 'cover_photo_width', 'cover_photo_flipped',
                  'photo_count_with_subalbums', 'cover_photo', 'geotagged_photo_count_with_subalbums',
                  'comments_count_with_subalbums', 'rephoto_count_with_subalbums', 'is_film_still_album',
                  'album_type')

    def get_album_type(self, instance):
        return instance.get_album_type


class PhotoSerializer(PhotoRepresentationSerializer):
    longitude = serializers.FloatField(source='lon')
    latitude = serializers.FloatField(source='lat')
    image = serializers.SerializerMethodField()
    full_image = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()
    favorited = serializers.SerializerMethodField()
    high_quality = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()

    def get_favorited(self, instance: Photo):
        print("get favorited")
        return instance.likes.exists()

    def get_high_quality(self, instance: Photo):
        print("get high_quality")
        if instance.height:
            return instance.height > 1080

        return False

    def get_full_image(self, instance):
        request = self.context['request']
        image_name = str(instance.image)
        prefix = 'uploads/'

        if image_name.startswith(prefix):
            image_name = image_name[len(prefix):]

        iiif_jpeg = request.build_absolute_uri(f'/iiif/work/iiif/ajapaik/{image_name}.tif/full/max/0/default.jpg')
        return iiif_jpeg

    def get_image(self, instance):
        request = self.context['request']
        relative_url = reverse('image_thumb', args=(instance.id,))

        return '{}[DIM]/'.format(request.build_absolute_uri(relative_url))

    def get_source(self, instance):
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

    class Meta(PhotoRepresentationSerializer.Meta):
        model = Photo
        fields = (
            *PhotoRepresentationSerializer.Meta.fields,
            'image', 'full_image', 'width', 'height', 'title',
            'author', 'source', 'latitude', 'longitude', 'azimuth',
            'favorited', 'high_quality', 'slug', 'comment_count',
            'rephoto_count'
        )


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ('description',)


class LicenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Licence
        fields = ('url', 'name', 'image_url')


class PhotoDetailsSerializer(PhotoRepresentationSerializer):
    lon = serializers.FloatField()
    lat = serializers.FloatField()
    full_image = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()
    rephotos = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    date_text = serializers.SerializerMethodField()
    in_selection = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    user_likes = serializers.SerializerMethodField()
    user_loves = serializers.SerializerMethodField()
    thumb_url = serializers.SerializerMethodField()
    source = SourceSerializer()
    licence = LicenceSerializer()

    def get_date_text(self, instance):
        if instance.date:
            return instance.date.strftime('%d-%m-%Y')
        else:
            return instance.date_text

    def get_full_image(self, instance):
        request = self.context['request']
        image_name = str(instance.image)
        prefix = 'uploads/'

        if image_name.startswith(prefix):
            image_name = image_name[len(prefix):]

        iiif_jpeg = request.build_absolute_uri(f'/iiif/work/iiif/ajapaik/{image_name}.tif/full/max/0/default.jpg')
        return iiif_jpeg

    def get_thumb_url(self, instance):
        request = self.context['request']
        relative_url = reverse('image_thumb', args=(instance.id, 1024, instance.get_pseudo_slug))

        return request.build_absolute_uri(relative_url)

    def get_date(self, instance):
        if instance.date:
            return instance.date.strftime('%d-%m-%Y')
        else:
            return instance.date_text

    def get_source(self, instance):
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

    def get_rephotos(self, instance):
        return RephotoSerializer(
            instance=instance.rephotos.all(),
            many=True,
            context={'request': self.context['request']},
        ).data

    def get_in_selection(self, instance):
        return instance.id in self.context['request'].session.get('photo_selection', [])

    def get_like_count(self, instance):
        return instance.likes.count()

    def get_user_likes(self, instance):
        return instance.likes.filter(level=1).exists()

    def get_user_loves(self, instance):
        return instance.likes.filter(level=2).exists()

    class Meta(PhotoRepresentationSerializer.Meta):
        model = Photo
        fields = (
            *PhotoRepresentationSerializer.Meta.fields, 'image', 'full_image', 'width', 'height', 'title', 'date',
            'author', 'source', 'azimuth', 'rephotos',
            'lat', 'lon', 'description',
            'slug', 'comment_count',
            'title',
            'address',
            'source_key',
            'source_url',
            'source',
            'licence',
            'in_selection', 'like_count', 'user_likes', 'user_loves', 'absolute_url', 'date_text', 'thumb_url'
        )


class PhotoDetailsSerializer(PhotoRepresentationSerializer):
    lon = serializers.FloatField()
    lat = serializers.FloatField()
    full_image = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()
    rephotos = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    date_text = serializers.SerializerMethodField()
    in_selection = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    user_likes = serializers.SerializerMethodField()
    user_loves = serializers.SerializerMethodField()
    thumb_url = serializers.SerializerMethodField()
    source = SourceSerializer()
    licence = LicenceSerializer()

    def get_date_text(self, instance):
        if instance.date:
            return instance.date.strftime('%d-%m-%Y')
        else:
            return instance.date_text

    def get_full_image(self, instance):
        request = self.context['request']
        image_name = str(instance.image)
        prefix = 'uploads/'

        if image_name.startswith(prefix):
            image_name = image_name[len(prefix):]

        iiif_jpeg = request.build_absolute_uri(f'/iiif/work/iiif/ajapaik/{image_name}.tif/full/max/0/default.jpg')
        return iiif_jpeg

    def get_thumb_url(self, instance):
        request = self.context['request']
        relative_url = reverse('image_thumb', args=(instance.id, 1024, instance.get_pseudo_slug))

        return request.build_absolute_uri(relative_url)

    def get_date(self, instance):
        if instance.date:
            return instance.date.strftime('%d-%m-%Y')
        else:
            return instance.date_text

    def get_source(self, instance):
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

    def get_rephotos(self, instance):
        return RephotoSerializer(
            instance=instance.rephotos.all(),
            many=True,
            context={'request': self.context['request']},
        ).data

    def get_in_selection(self, instance):
        return instance.id in self.context['request'].session.get('photo_selection', [])

    def get_like_count(self, instance):
        return instance.likes.count()

    def get_user_likes(self, instance):
        return instance.likes.filter(level=1).exists()

    def get_user_loves(self, instance):
        return instance.likes.filter(level=2).exists()

    class Meta(PhotoRepresentationSerializer.Meta):
        model = Photo
        fields = (
            *PhotoRepresentationSerializer.Meta.fields, 'image', 'full_image', 'width', 'height', 'title', 'date',
            'author', 'source', 'azimuth', 'rephotos',
            'lat', 'lon', 'description',
            'slug', 'comment_count',
            'title',
            'address',
            'source_key',
            'source_url',
            'source',
            'licence',
            'in_selection', 'like_count', 'user_likes', 'user_loves', 'absolute_url', 'date_text', 'thumb_url'
        )


class PhotoWithDistanceSerializer(PhotoSerializer):
    distance = serializers.IntegerField(source='distance.m', read_only=True)

    class Meta(PhotoSerializer.Meta):
        fields = (
            'id', 'distance', 'image', 'width', 'height', 'title', 'date',
            'author', 'source', 'latitude', 'longitude', 'azimuth', 'rephotos',
            'favorited',
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

    def get_date(self, instance):
        if instance.date:
            return instance.date.strftime('%d-%m-%Y')
        else:
            return instance.date_text

    def get_source(self, instance):
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


class GalleryResultsSerializer(DataclassSerializer):
    album = AlbumMiniSerializer()
    fb_share_photos = PhotoMiniSerializer(many=True)
    photos = PhotoSerializer(many=True)
    photos_with_comments = PhotoSerializer(many=True)
    photos_with_rephotos = PhotoSerializer(many=True)
    videos = VideoSerializer(many=True)

    class Meta:
        dataclass = GalleryResults


class ImageSimilaritySerializer(serializers.ModelSerializer):
    from_photo = PhotoMiniSerializer()
    to_photo = PhotoRepresentationSerializer()

    class Meta:
        model = ImageSimilarity
        fields = ('id', 'from_photo', 'to_photo', 'similarity_type')


class APIPhotoSerializer(serializers.ModelSerializer):
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

    def get_display_text(self, instance):
        return instance.get_display_text

    def get_full_image(self, instance):
        request = self.context['request']
        image_name = str(instance.image)
        prefix = 'uploads/'

        if image_name.startswith(prefix):
            image_name = image_name[len(prefix):]

        iiif_jpeg = request.build_absolute_uri(f'/iiif/work/iiif/ajapaik/{image_name}.tif/full/max/0/default.jpg')
        return iiif_jpeg

    def get_image(self, instance):
        request = self.context['request']
        relative_url = reverse('image_thumb', args=(instance.id,))

        return '{}[DIM]/'.format(request.build_absolute_uri(relative_url))

    def get_date(self, instance):
        if instance.date:
            return instance.date.strftime('%d-%m-%Y')
        else:
            return instance.date_text

    def get_source(self, instance):
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

    def get_rephotos(self, instance):
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
