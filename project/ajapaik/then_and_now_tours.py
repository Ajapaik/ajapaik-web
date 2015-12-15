import datetime
import json
import random

from django import forms
from django.contrib.auth import logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.utils.timezone import utc
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from registration.forms import RegistrationFormUniqueEmail
from registration.signals import user_registered
from sorl.thumbnail import get_thumbnail, delete

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


class TourSelectionForm(forms.Form):
    tour = forms.ModelChoiceField(queryset=Tour.objects.all())


class UserRegistrationForm(RegistrationFormUniqueEmail):
    username = forms.CharField(max_length=254, required=False, widget=forms.HiddenInput())
    first_name = forms.CharField(label=_('First name'), max_length=30)
    last_name = forms.CharField(label=_('Last name'), max_length=30)

    def clean_email(self):
        email = self.cleaned_data['email']
        self.cleaned_data['username'] = email
        return email


def user_created(sender, user, request, **kwargs):
    form = UserRegistrationForm(request.POST)
    user = User.objects.filter(username=form.data['email']).first()
    if user:
        user.first_name = form.data['first_name']
        user.last_name = form.data['last_name']
        user.save()

user_registered.connect(user_created)


def user_has_confirmed_email(user):
    ok = True
    if not hasattr(user, 'email'):
        ok = False
    else:
        if not user.email:
            ok = False
    return ok and user.is_active


def frontpage(request):
    if request.user:
        if not hasattr(request.user, 'email'):
            logout(request)
        else:
            if not request.user.email:
               logout(request)
    ret = {
        'is_frontpage': True,
        'recent_photos': TourRephoto.objects.order_by('-created')[:5]
    }

    return render_to_response('then_and_now/frontpage.html', RequestContext(request, ret))


@user_passes_test(user_has_confirmed_email, login_url='/accounts/login/')
def map_view(request, tour_id=None):
    ret = {
        'photos': []
    }
    profile = request.get_user().profile
    if not tour_id:
        generation_form = RandomTourForm(request.GET)
        selection_form = TourSelectionForm(request.GET)
        if selection_form.is_valid():
            tour = selection_form.cleaned_data['tour']

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


@user_passes_test(user_has_confirmed_email, login_url='/accounts/login/')
def gallery(request, tour_id):
    ret = {
        'is_gallery': True
    }
    tour = Tour.objects.filter(pk=tour_id).first()
    profile = request.user.profile
    if tour:
        ret['tour'] = tour
        photos = tour.photos.order_by('tourphoto__order').annotate(rephoto_count=Count('tourrephoto'))
        # for each in photos:
        #     each.user_has_rephotographed = each.tourrephoto.filter(user=profile).exists()
        ret['photos'] = photos

    return render_to_response('then_and_now/gallery.html', RequestContext(request, ret))


@user_passes_test(user_has_confirmed_email, login_url='/accounts/login/')
def detail(request, tour_id, photo_id, rephoto_id=None):
    photo = get_object_or_404(Photo, id=photo_id)
    rp = None
    if rephoto_id:
        rp = get_object_or_404(TourRephoto, id=rephoto_id)
    tour = get_object_or_404(Tour, id=tour_id)
    tour_photo_order = list(TourPhoto.objects.filter(tour=tour).order_by('order').values_list('photo_id', flat=True))
    rephoto_order = list(TourRephoto.objects.filter(tour=tour, original=photo).order_by('created').values_list('id', flat=True))
    current_photo_index = tour_photo_order.index(photo.id)
    ret = {
        'photo': photo,
        'rephoto': rp,
        'tour': tour,
        'rephotos': TourRephoto.objects.filter(original=photo, tour=tour),
        'is_detail': True
    }
    if (len(tour_photo_order) - 1) > current_photo_index:
        ret['next_photo'] = Photo.objects.filter(id=tour_photo_order[current_photo_index + 1]).first()
    if current_photo_index > 0:
        ret['previous_photo'] = Photo.objects.filter(id=tour_photo_order[current_photo_index - 1]).first()
    if rp:
        current_rephoto_index = rephoto_order.index(rp.id)
        if (len(rephoto_order) - 1) > current_rephoto_index:
            ret['next_rephoto'] = TourRephoto.objects.filter(id=rephoto_order[current_rephoto_index + 1]).first()
        if current_rephoto_index > 0:
            ret['previous_rephoto'] = TourRephoto.objects.filter(id=rephoto_order[current_rephoto_index - 1]).first()

    return render_to_response('then_and_now/detail.html', RequestContext(request, ret))


@user_passes_test(user_has_confirmed_email, login_url='/accounts/login/')
def rephoto_thumb(request, rephoto_id=None, thumb_size=250, pseudo_slug=None):
    p = get_object_or_404(TourRephoto, id=rephoto_id)
    thumb_size = int(thumb_size)
    if 0 < thumb_size <= 150:
        thumb_size = 150
    elif 300 < thumb_size <= 500:
        thumb_size = 400
    elif 500 < thumb_size <= 800:
        thumb_size = 800
    else:
        thumb_size = 250

    thumb_str = str(thumb_size) + 'x' + str(thumb_size)
    original_thumb = get_thumbnail(p.original.image, thumb_str, upscale=False)
    thumb_str = str(original_thumb.size[0]) + 'x' + str(original_thumb.size[1])
    im = get_thumbnail(p.image, thumb_str, upscale=True, downscale=True, crop='center')
    try:
        content = im.read()
    except IOError:
        delete(im)
        im = get_thumbnail(p.image, thumb_str, upscale=False)
        content = im.read()

    return HttpResponse(content, content_type='image/jpg')


@user_passes_test(user_has_confirmed_email, login_url='/accounts/login/')
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


@user_passes_test(user_has_confirmed_email, login_url='/accounts/login/')
def tour_complete(request, tour_id):
    tour = Tour.objects.filter(pk=tour_id).first()
    ret = {
        'tour': tour,
        'minutes': (datetime.datetime.utcnow().replace(tzinfo=utc) - tour.created.replace(tzinfo=utc)).seconds / 60
    }

    return render_to_response('then_and_now/tour_complete.html', RequestContext(request, ret))
