import math

import operator

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.core.urlresolvers import reverse
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django import forms

from project.ajapaik.models import Tour, Photo, TourPhoto
from project.ajapaik.settings import THEN_AND_NOW_TOUR_RANDOM_PHOTO_MIN_DIST, THEN_AND_NOW_TOUR_RANDOM_PHOTO_MAX_DIST, \
    THEN_AND_NOW_TOUR_DEFAULT_PHOTO_COUNT


class random_tour_form(forms.Form):
    lat = forms.FloatField(min_value=-85.05115, max_value=85)
    lng = forms.FloatField(min_value=-180, max_value=180)
    min_distance = forms.FloatField(required=False)
    max_distance = forms.FloatField(required=False)
    how_many = forms.IntegerField(required=False)


@api_view(['GET'])
@permission_classes((AllowAny,))
def random_tour(request):
    form = random_tour_form(request.GET)
    ret = {
        'photos': []
    }
    if form.is_valid():
        user_lat = form.cleaned_data['lat']
        user_lng = form.cleaned_data['lng']
        max_dist = form.cleaned_data['max_distance']
        min_dist = form.cleaned_data['min_distance']
        how_many = form.cleaned_data['how_many']
        if not max_dist:
            max_dist = THEN_AND_NOW_TOUR_RANDOM_PHOTO_MAX_DIST
        if not min_dist:
            min_dist = THEN_AND_NOW_TOUR_RANDOM_PHOTO_MIN_DIST
        if not how_many:
            how_many = THEN_AND_NOW_TOUR_DEFAULT_PHOTO_COUNT
        offset = float(min_dist + max_dist) / 2.00 / 111138.56
        offset_location = Point(user_lng, user_lat + offset)
        photo_set = Photo.objects.filter(rephoto_of__isnull=True,
                                         geography__distance_lte=(offset_location, D(m=max_dist)),
                                         geography__distance_gte=(offset_location, D(m=min_dist)),
        )
        total = photo_set.count()
        for each in photo_set:
            dx = each.lat - offset_location[1]
            dy = each.lon - offset_location[0]
            each.user_angle = math.atan2(dy, dx)
        ordered = sorted(photo_set, key=operator.attrgetter('user_angle'))
        sample = []
        divisor = math.ceil(total / how_many)
        for k, v in enumerate(ordered):
            if k % divisor == 0:
                sample.append(v)
        #tour = None
        #if len(sample) > 0:
            #tour = Tour(
             #   name='Random tour'
            #)
            #tour.save()
        #i = 0
        for each in sample:
            #if tour:
                #TourPhoto(
                    #tour=tour,
                    #photo=each,
                    #order=i
                #).save()
                #i += 1
            ret['photos'].append({
                'name': each.description,
                'lat': each.lat,
                'lng': each.lon,
                'azimuth': each.azimuth,
                'image': request.build_absolute_uri(reverse('project.ajapaik.views.image_thumb',
                                            args=(each.pk, 800, each.get_pseudo_slug())))
            })
    else:
        ret['errors'] = form.errors

    return Response(ret)


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_tour(request, id):
    tour = Tour.objects.filter(pk=id).first()
    ret = {
        'photos': [],
    }
    if tour:
        for p in tour.photos.order_by('tourphoto__order'):
            ret['photos'].append({
                'name': p.description,
                'lat': p.lat,
                'lng': p.lon,
                'azimuth': p.azimuth,
                'image': request.build_absolute_uri(reverse('project.ajapaik.views.image_thumb',
                                                            args=(p.pk, 800, p.get_pseudo_slug())))
            })

    return Response(ret)
