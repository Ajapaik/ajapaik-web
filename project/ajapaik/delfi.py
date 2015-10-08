from django.contrib.gis.gdal import SpatialReference, CoordTransform
from django.contrib.gis.measure import D
from django.core.urlresolvers import reverse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from project.ajapaik.forms import DelfiBboxRequestForm, DelfiPhotoInfoRequestForm
from project.ajapaik.models import Photo
from django.contrib.gis.geos import Point


@api_view(['GET'])
@permission_classes((AllowAny,))
def photos_bbox(request):
    form = DelfiBboxRequestForm(request.query_params)
    if form.is_valid():
        ref_location = Point(x=(form.cleaned_data['top_left'].x + form.cleaned_data['bottom_right'].x) / 2,
                             y=(form.cleaned_data['bottom_right'].y + form.cleaned_data['top_left'].y) / 2, srid=4326)
        print form.cleaned_data['top_left']
        print form.cleaned_data['bottom_right']
        print ref_location.y
        print ref_location.x
        qs = Photo.objects.filter(rephoto_of__isnull=True, lat__isnull=False, lon__isnull=False,
                                  lat__gte=form.cleaned_data['top_left'].y,
                                  lon__gte=form.cleaned_data['top_left'].x,
                                  lat__lte=form.cleaned_data['bottom_right'].y,
                                  lon__lte=form.cleaned_data['bottom_right'].x).filter(
            geography__distance_lte=(ref_location, D(m=3000)))
        our_ref = SpatialReference(4326)
        delfi_ref = SpatialReference(3301)
        trans = CoordTransform(our_ref, delfi_ref)
        photos = []
        for p in qs:
            location = Point(x=p.lon, y=p.lat, srid=4326)
            location.transform(trans)
            photos.append({
                'id': p.id,
                'latitude': location.y,
                'longitude': location.x,
                'description': p.description,
            })

        return Response(photos)

    return Response([])


@api_view(['GET'])
@permission_classes((AllowAny,))
def photo_info(request):
    form = DelfiPhotoInfoRequestForm(request.query_params)
    if form.is_valid():
        photo = form.cleaned_data['id']
        our_ref = SpatialReference(4326)
        delfi_ref = SpatialReference(3301)
        trans = CoordTransform(our_ref, delfi_ref)
        location = Point(x=photo.lon, y=photo.lat, srid=4326)
        location.transform(trans)

        return Response({
            'id': photo.id,
            'author': photo.author,
            'description': photo.description,
            'latitude': location.y,
            'longitude': location.x,
            'source': photo.source.description + ' ' + photo.source_key,
            'url': request.build_absolute_uri(reverse('project.ajapaik.views.photoslug', args=(photo.id, photo.get_pseudo_slug()))),
            'thumbUrl': request.build_absolute_uri(reverse('project.ajapaik.views.photo_thumb', args=(photo.id, 400)))
        })

    return Response({})
