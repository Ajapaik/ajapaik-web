import datetime
import json
import random

from django import forms
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.utils.timezone import utc
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt

from project.ajapaik.models import TourRephoto, Photo, Tour, TourPhoto, Album, AlbumPhoto
from project.ajapaik.settings import THEN_AND_NOW_TOUR_RANDOM_PHOTO_MAX_DIST, THEN_AND_NOW_TOUR_DEFAULT_PHOTO_COUNT, THEN_AND_NOW_TOUR_RANDOM_PHOTO_MIN_DIST


class CameraUploadForm(forms.Form):
    image = forms.ImageField()
    tour = forms.ModelChoiceField(Tour.objects.all())
    original = forms.ModelChoiceField(Photo.objects.all())


class RandomTourForm(forms.Form):
    lat = forms.FloatField(min_value=-85.05115, max_value=85)
    lng = forms.FloatField(min_value=-180, max_value=180)
    min_distance = forms.FloatField(required=False)
    max_distance = forms.FloatField(required=False)
    how_many = forms.IntegerField(required=False)


class AlbumSelectionForm(forms.Form):
    album = forms.ModelChoiceField(queryset=Album.objects.filter(atype=Album.CURATED))


def frontpage(request):
    ret = {
        'is_frontpage': True,
        'recent_photos': TourRephoto.objects.order_by('-created')[:5]
    }

    return render_to_response('then_and_now/frontpage.html', RequestContext(request, ret))


def map_view(request, tour_id=None):
    ret = {
        'photos': []
    }
    profile = request.get_user().profile
    if not tour_id:
        generation_form = RandomTourForm(request.GET)
        selection_form = AlbumSelectionForm(request.GET)
        if selection_form.is_valid():
            a = selection_form.cleaned_data['album']
            tour = Tour(
                name=_('Tour of album "%(album)s" for %(user)s') % {'album': a.name, 'user': profile.user_id},
                user=profile
            )
            if a.ordered:
                tour.ordered = True
            tour.save()
            album_photo_order = list(AlbumPhoto.objects.filter(album=a).order_by('created').values_list('photo_id', flat=True))
            photo_set = a.photos.filter(lat__isnull=False, lon__isnull=False)
            for each in photo_set:
                if tour:
                    TourPhoto(
                            tour=tour,
                            photo=each,
                            order=album_photo_order.index(each.id)
                    ).save()

            return redirect(reverse('project.ajapaik.then_and_now_tours.map_view', args=(tour.pk,)))
        else:
            if generation_form.is_valid():
                user_lat = generation_form.cleaned_data['lat']
                user_lng = generation_form.cleaned_data['lng']
                max_dist = generation_form.cleaned_data['max_distance']
                min_dist = generation_form.cleaned_data['min_distance']
                how_many = generation_form.cleaned_data['how_many']
                user_location = Point(user_lng, user_lat)
                if not min_dist:
                    min_dist = THEN_AND_NOW_TOUR_RANDOM_PHOTO_MIN_DIST
                if not max_dist:
                    max_dist = THEN_AND_NOW_TOUR_RANDOM_PHOTO_MAX_DIST
                if not how_many:
                    how_many = THEN_AND_NOW_TOUR_DEFAULT_PHOTO_COUNT
                photo_set = Photo.objects.filter(rephoto_of__isnull=True,
                                                 geography__distance_lte=(user_location, D(m=max_dist)),
                                                 geography__distance_gte=(user_location, D(m=min_dist)), )
                total = photo_set.count()
                if how_many <= total:
                    sample = random.sample(photo_set, how_many)
                else:
                    sample = random.sample(photo_set, total)
                tour = Tour(
                        name=_('Random Tour'),
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
                ret['errors'] = generation_form.errors
                return redirect(reverse('project.ajapaik.then_and_now_tours.frontpage'))
    else:
        tour = Tour.objects.filter(pk=tour_id).first()
        tour_photo_order = list(TourPhoto.objects.filter(tour=tour).order_by('order').values_list('photo_id', flat=True))
        for each in tour.photos.all():
            ret['photos'].append({
                'name': each.description,
                'order': tour_photo_order.index(each.id),
                'lat': each.lat,
                'lng': each.lon,
                'azimuth': each.azimuth,
                'image': request.build_absolute_uri(
                    reverse('project.ajapaik.views.image_thumb', args=(each.pk, 50, each.get_pseudo_slug()))),
                'url': request.build_absolute_uri(
                    reverse('project.ajapaik.then_and_now_tours.detail', args=(each.pk, tour.pk))),
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
    photo = Photo.objects.filter(pk=photo_id).first()
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
    ret = {}
    profile = request.get_user().profile
    form = CameraUploadForm(request.POST, request.FILES)
    if form.is_valid():
        tour = form.cleaned_data['tour']
        TourRephoto(
                image=form.cleaned_data['image'],
                original=form.cleaned_data['original'],
                tour=tour,
                user=profile
        ).save()
        each_photo_done = True
        for each in tour.photos.all():
            if not TourRephoto.objects.filter(tour=tour, original=each, user=profile).exists():
                each_photo_done = False
                break
        if each_photo_done:
            return redirect(reverse('project.ajapaik.then_and_now_tours.tour_complete', args=(tour.pk,)))
        else:
            return redirect(reverse('project.ajapaik.then_and_now_tours.map_view', args=(tour.pk,)))

    return HttpResponse(ret)


def tour_complete(request, tour_id):
    tour = Tour.objects.filter(pk=tour_id).first()
    ret = {
        'tour': tour,
        'minutes': (datetime.datetime.utcnow().replace(tzinfo=utc) - tour.created.replace(tzinfo=utc)).seconds / 60
    }

    return render_to_response('then_and_now/tour_complete.html', RequestContext(request, ret))


def create_assignment(request):
    ret = {}

    return render_to_response('then_and_now/create_assignment.html', RequestContext(request, ret))
