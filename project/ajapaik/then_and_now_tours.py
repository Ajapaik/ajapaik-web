import json
import math

import operator
import random

import datetime
from time import timezone

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django.utils.timezone import utc
from django.views.decorators.csrf import csrf_exempt
from django import forms

from project.ajapaik.models import TourRephoto, Photo, Tour, TourPhoto
from project.ajapaik.settings import THEN_AND_NOW_TOUR_RANDOM_PHOTO_MAX_DIST, THEN_AND_NOW_TOUR_DEFAULT_PHOTO_COUNT
from project.ajapaik.settings import THEN_AND_NOW_TOUR_RANDOM_PHOTO_MIN_DIST


class camera_upload_form(forms.Form):
    image = forms.ImageField()
    tour = forms.ModelChoiceField(Tour.objects.all())
    original = forms.ModelChoiceField(Photo.objects.all())


class random_tour_form(forms.Form):
    lat = forms.FloatField(min_value=-85.05115, max_value=85)
    lng = forms.FloatField(min_value=-180, max_value=180)
    min_distance = forms.FloatField(required=False)
    max_distance = forms.FloatField(required=False)
    how_many = forms.IntegerField(required=False)


def frontpage(request):
    ret = {
        'is_frontpage': True,
        'recent_photos': TourRephoto.objects.order_by('-created')[:5]
    }
    return render_to_response('then_and_now/frontpage.html', RequestContext(request, ret))

'''
def map_view(request, tour_id=None):
    ret = {
        'photos': []
    }
    if not tour_id:
        form = random_tour_form(request.GET)
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
            tour = None
            if len(sample) > 0:
                tour = Tour(
                    name='Random tour',
                    user_lat=user_lat,
                    user_lng=user_lng,
                )
                tour.save()
            i = 0
            for each in sample:
                if tour:
                    TourPhoto(
                        tour=tour,
                        photo=each,
                        order=i
                    ).save()
                i += 1
            return redirect(reverse('project.ajapaik.then_and_now_tours.map_view', args=(tour.pk,)))
        else:
            ret['errors'] = form.errors
    else:
        tour = Tour.objects.filter(pk=tour_id).first()
        for each in tour.photos.all():
            ret['photos'].append({
                'name': each.description,
                'lat': each.lat,
                'lng': each.lon,
                'azimuth': each.azimuth,
                'image': request.build_absolute_uri(reverse('project.ajapaik.views.image_thumb',
                                                            args=(each.pk, 800, each.get_pseudo_slug()))),
                'url': request.build_absolute_uri(reverse('project.ajapaik.then_and_now_tours.detail',
                                                            args=(each.pk,)))
            })
        ret['photos'] = json.dumps(ret['photos'])
        ret['tour'] = tour
        ret['is_map'] = True

    return render_to_response('then_and_now/map.html', RequestContext(request, ret))
'''


def map_view(request, tour_id=None):
    ret = {
        'photos': []
    }
    profile = request.get_user().profile
    if not tour_id:
        form = random_tour_form(request.GET)
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
            user_location = Point(user_lng, user_lat)
            photo_set = Photo.objects.filter(rephoto_of__isnull=True,
                                             geography__distance_lte=(user_location, D(m=max_dist)),
                                             geography__distance_gte=(user_location, D(m=min_dist)),
                                             )
            sample = random.sample(photo_set, how_many)
            tour = None
            if len(sample) > 0:
                tour = Tour(
                    name='Random tour',
                    user_lat=user_lat,
                    user_lng=user_lng,
                    user=profile
                )
                tour.save()
            i = 0
            for each in sample:
                if tour:
                    TourPhoto(
                        tour=tour,
                        photo=each,
                        order=i
                    ).save()
                i += 1
            return redirect(reverse('project.ajapaik.then_and_now_tours.map_view', args=(tour.pk,)))
        else:
            ret['errors'] = form.errors
    else:
        tour = Tour.objects.filter(pk=tour_id).first()
        for each in tour.photos.all():
            ret['photos'].append({
                'name': each.description,
                'name': each.description,
                'lat': each.lat,
                'lng': each.lon,
                'azimuth': each.azimuth,
                'image': request.build_absolute_uri(reverse('project.ajapaik.views.image_thumb',
                                                            args=(each.pk, 50, each.get_pseudo_slug()))),
                'url': request.build_absolute_uri(reverse('project.ajapaik.then_and_now_tours.detail',
                                                            args=(each.pk, tour.pk))),
                'isDone': TourRephoto.objects.filter(original=each, tour=tour, user=profile).exists()
            })
        ret['photos'] = json.dumps(ret['photos'])
        ret['tour'] = tour
        ret['is_map'] = True

    return render_to_response('then_and_now/map.html', RequestContext(request, ret))


def gallery(request, tour_id):
    ret = {
        'is_gallery': True
    }
    tour = Tour.objects.filter(pk=tour_id).first()
    if tour:
        ret['tour'] = tour

    return render_to_response('then_and_now/gallery.html', RequestContext(request, ret))


def detail(request, photo_id, tour_id):
    photo = Photo.objects.filter(pk=photo_id).order_by('-created').first()
    tour = Tour.objects.filter(pk=tour_id).first()
    profile = request.get_user().profile
    ret = {
        'photo': photo,
        'tour': tour,
        'rephoto': TourRephoto.objects.filter(original=photo, user=profile, tour=tour)
    }

    return render_to_response('then_and_now/detail.html', RequestContext(request, ret))


def pair(request, original_photo_id, rephoto_id):
    ret = {

    }

    return render_to_response('then_and_now/pair.html', RequestContext(request, ret))


@csrf_exempt
def camera_upload(request):
    ret = {

    }
    profile = request.get_user().profile
    form = camera_upload_form(request.POST, request.FILES)
    if form.is_valid():
        tour = form.cleaned_data['tour']
        TourRephoto(
            image=form.cleaned_data['image'],
            original=form.cleaned_data['original'],
            tour=form.cleaned_data['tour'],
            user=profile
        ).save()
        each_photo_done = True
        for each in tour.photos.prefetch_related('tour_rephotos'):
            if not each.tour_rephotos.filter().exists():
                each_photo_done = False
                break
        if each_photo_done:
            return redirect(reverse('project.ajapaik.then_and_now_tours.tour_complete', args=(tour.pk,)))
    else:
        ret['errors'] = form.errors

    return HttpResponse(ret)


def tour_complete(request, tour_id):
    tour = Tour.objects.filter(pk=tour_id).first()
    ret = {
        'tour': tour,
        'minutes': (datetime.datetime.utcnow().replace(tzinfo=utc) - tour.created.replace(tzinfo=utc)).seconds / 60
    }

    return render_to_response('then_and_now/tour_complete.html', RequestContext(request, ret))


def juhan(request):
    ret = {

    }
    return render_to_response('then_and_now/google.html', RequestContext(request, ret))
