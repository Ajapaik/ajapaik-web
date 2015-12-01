from django.core.urlresolvers import reverse
from django.utils.translation import activate
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from project.ajapaik.models import Album, Photo

RANDOM_SET_SIZE = 200

class MerekultuurPhotoSerializer(serializers.ModelSerializer):
    source = serializers.CharField(source='source_string')
    thumbUrl = serializers.URLField(source='thumb_url')
    fullSizeUrl = serializers.URLField(source='full_size_url')
    ajapaikUrl = serializers.URLField(source='ajapaik_url')

    class Meta:
        model = Photo
        fields = ('author', 'description', 'source', 'thumbUrl', 'fullSizeUrl', 'ajapaikUrl')

@api_view(['GET'])
@permission_classes((AllowAny,))
def get_photos(request):
    activate('et')
    album = Album.objects.filter(pk=3089).first()
    ret = []
    if album:
        pqs = album.get_historic_photos_queryset_with_subalbums().prefetch_related('source')[:RANDOM_SET_SIZE]
        for p in pqs:
            p.source_string = p.source.description + ' ' + p.source_key
            p.thumb_url = request.build_absolute_uri(
                reverse('project.ajapaik.views.image_thumb', args=(p.pk, 400, p.get_pseudo_slug()))
            )
            p.full_size_url = request.build_absolute_uri(
                reverse('project.ajapaik.views.image_full', args=(p.pk, p.get_pseudo_slug()))
            )
            p.ajapaik_url = request.build_absolute_uri(
                reverse('project.ajapaik.views.photoslug', args=(p.pk, p.get_pseudo_slug()))
            )
        ret = MerekultuurPhotoSerializer(pqs, many=True).data

    return Response(ret)