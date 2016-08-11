from django.contrib.gis.gdal import SpatialReference, CoordTransform
from django.core.urlresolvers import reverse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from project.ajapaik.models import Photo
from django.contrib.gis.geos import Point
from django import forms
from django.utils.translation import ugettext as _


class DelfiBboxRequestForm(forms.Form):
    bbox = forms.CharField()

    def clean(self):
        cleaned_data = super(DelfiBboxRequestForm, self).clean()
        bbox_str = cleaned_data.get('bbox')
        if not bbox_str:
            raise forms.ValidationError(_('Bounding box must be set'))
        bbox_parts = bbox_str.split(',')
        if len(bbox_parts) != 4:
            raise forms.ValidationError(_('Bounding box must have 4 comma-separated members'))
        else:
            try:
                bbox_parts = [float(x) for x in bbox_parts]
            except:
                raise forms.ValidationError(_('Bounding box values must be numbers'))
            our_ref = SpatialReference(4326)
            delfi_ref = SpatialReference(3301)
            trans = CoordTransform(delfi_ref, our_ref)
            top_left = Point(y=bbox_parts[1], x=bbox_parts[0], srid=3301)
            bottom_right = Point(y=bbox_parts[3], x=bbox_parts[2], srid=3301)
            top_left.transform(trans)
            bottom_right.transform(trans)
            cleaned_data['top_left'] = top_left
            cleaned_data['bottom_right'] = bottom_right

        return cleaned_data


class DelfiPhotoInfoRequestForm(forms.Form):
    id = forms.ModelChoiceField(queryset=Photo.objects.filter(rephoto_of__isnull=True))

@api_view(['GET'])
@permission_classes((AllowAny,))
def photos_bbox(request):
    form = DelfiBboxRequestForm(request.query_params)
    if form.is_valid():
        qs = Photo.objects.filter(rephoto_of__isnull=True, lat__isnull=False, lon__isnull=False, confidence__gte=0.2,
                                  lat__gte=form.cleaned_data['top_left'].y,
                                  lon__gte=form.cleaned_data['top_left'].x,
                                  lat__lte=form.cleaned_data['bottom_right'].y,
                                  lon__lte=form.cleaned_data['bottom_right'].x).order_by('?')[:500]
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

        source_str = ''
        if photo.source and photo.source_key:
            source_str = photo.source.description + ' ' + photo.source_key

        return Response({
            'id': photo.id,
            'author': photo.author,
            'description': photo.description,
            'latitude': location.y,
            'longitude': location.x,
            'source': source_str,
            'url': request.build_absolute_uri(reverse('project.ajapaik.views.photoslug',
                                                      args=(photo.id, photo.get_pseudo_slug()))),
            'thumbUrl': request.build_absolute_uri(reverse('project.ajapaik.views.image_thumb',
                                                           args=(photo.id, 400, photo.get_pseudo_slug())))
        })

    return Response({})
