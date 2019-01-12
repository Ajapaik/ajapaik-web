from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.serializers import ModelSerializer, IntegerField, CharField, SerializerMethodField

from ajapaik.ajapaik.models import Photo


class ResultSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500


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
            'id', 'ajapaik_url', 'description', 'author', 'date', 'source_description', 'source_key', 'source_url',
            'lat',
            'lon', 'azimuth', 'geotag_count')


class PhotosView(ListAPIView):
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
