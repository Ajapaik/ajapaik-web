from rest_framework import viewsets, serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ajapaik.ajapaik.models import Photo, GeoTag


class GeoTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeoTag
        fields = '__all__'


class RephotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = '__all__'


class PhotoSerializer(serializers.ModelSerializer):
    rephotos = RephotoSerializer(many=True, read_only=True)
    geotags = serializers.SerializerMethodField()

    def get_geotags(self, obj):
        request = self.context.get('request')

        return request.build_absolute_uri('/photos/%d/geotags/' % obj.id)

    class Meta:
        model = Photo
        fields = '__all__'


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.filter(rephoto_of__isnull=True)
    serializer_class = PhotoSerializer


class PhotoGeoTagViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)

    def retrieve(self, request, pk=None):
        queryset = GeoTag.objects.filter(photo__pk=pk)
        serializer = GeoTagSerializer(queryset, many=True)

        return Response(serializer.data)
