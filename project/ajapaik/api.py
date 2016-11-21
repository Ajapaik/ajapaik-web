import dateutil.parser
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.serializers import ModelSerializer, IntegerField, CharField, SerializerMethodField

from project.ajapaik.models import Photo


class ResultSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500


# Serializers
class BboxResponseSerializer(ModelSerializer):
    geotag_count = IntegerField(source='geotags.count')
    source_description = CharField(source='source.description')
    ajapaik_url = SerializerMethodField()

    def get_ajapaik_url(self, obj):
        relative_url = obj.get_absolute_url()
        return self.context['request'].build_absolute_uri(relative_url)

    class Meta:
        model = Photo
        fields = (
            'id', 'ajapaik_url', 'title', 'author', 'date', 'source_description', 'source_key', 'source_url',
            'lat', 'lon', 'azimuth', 'geotag_count')


class ChangedResponseSerializer(ModelSerializer):
    geotag_count = IntegerField(source='geotags.count')
    source_description = CharField(source='source.description')
    fotodugnad_url = SerializerMethodField()

    def get_fotodugnad_url(self, obj):
        relative_url = obj.get_absolute_url()
        return self.context['request'].build_absolute_uri(relative_url)

    class Meta:
        model = Photo
        fields = (
            'id', 'created', 'modified', 'source_description', 'external_id', 'source_url',
            'lat', 'lon', 'azimuth', 'geotag_count', 'fotodugnad_url')


# CBVs
class PhotosBboxView(ListAPIView):
    queryset = Photo.objects.all()
    serializer_class = BboxResponseSerializer
    pagination_class = ResultSetPagination

    def get_queryset(self):
        queryset = Photo.objects.filter(rephoto_of__isnull=True, lat__isnull=False, lon__isnull=False)
        sw_lat = self.request.query_params.get('sw-lat', None)
        sw_lon = self.request.query_params.get('sw-lon', None)
        ne_lat = self.request.query_params.get('ne-lat', None)
        ne_lon = self.request.query_params.get('ne-lon', None)
        if sw_lat and sw_lon and ne_lat and ne_lon:
            queryset = queryset.filter(
                lat__gte=sw_lat,
                lon__gte=sw_lon,
                lat__lte=ne_lat,
                lon__lte=ne_lon
            )

        return queryset


class PhotosChangedView(ListAPIView):
    queryset = Photo.objects.all()
    serializer_class = ChangedResponseSerializer
    pagination_class = ResultSetPagination

    def get_queryset(self):
        changed_since = self.request.query_params.get('modified', None)
        queryset = Photo.objects.filter(rephoto_of__isnull=True)
        if changed_since:
            queryset = queryset.filter(modified__gte=dateutil.parser.parse(changed_since))

        return queryset.order_by('-modified')
