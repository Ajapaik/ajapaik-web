import datetime
import json
import random

import autocomplete_light
from django import forms
from django.contrib.auth import logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.core.urlresolvers import reverse
from django.db.models import Count, F
from django.forms import inlineformset_factory, TypedMultipleChoiceField
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.utils.timezone import utc
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from registration.forms import RegistrationFormUniqueEmail
from registration.signals import user_registered
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from sorl.thumbnail import get_thumbnail, delete

from project.ajapaik.models import TourRephoto, Photo, Tour, TourPhotoOrder, TourGroup, Profile, Licence
from project.ajapaik.settings import THEN_AND_NOW_TOUR_RANDOM_PHOTO_MAX_DIST, THEN_AND_NOW_TOUR_DEFAULT_PHOTO_COUNT, \
    THEN_AND_NOW_TOUR_RANDOM_PHOTO_MIN_DIST


# Forms
class CameraUploadForm(forms.Form):
    image = forms.ImageField()
    tour = forms.ModelChoiceField(Tour.objects.all())
    original = forms.ModelChoiceField(Photo.objects.all())


class RandomTourForm(forms.Form):
    lat = forms.FloatField(min_value=-85.05115, max_value=85)
    lng = forms.FloatField(min_value=-180, max_value=180)
    min_distance = forms.FloatField(required=False)
    max_distance = forms.FloatField(required=False)
    random_count = forms.IntegerField(required=False)


class ChooseNewTourTypeForm(forms.Form):
    OPEN, FIXED, NEARBY_RANDOM = range(3)
    TYPE_CHOICES = (
        (OPEN, _('Open tour')),
        (FIXED, _('Fixed photo set')),
        (NEARBY_RANDOM, _('Random with nearby pictures')),
    )
    tour_type = forms.ChoiceField(choices=TYPE_CHOICES, label=_('Tour type'))
    random_count = forms.IntegerField(required=False, label=_('Number of random pictures'))
    lat = forms.FloatField(min_value=-85.05115, max_value=85, required=False, widget=forms.HiddenInput())
    lng = forms.FloatField(min_value=-180, max_value=180, required=False, widget=forms.HiddenInput())

    def clean(self):
        self.cleaned_data['tour_type'] = int(self.cleaned_data['tour_type'])
        if self.cleaned_data['tour_type'] == self.NEARBY_RANDOM and (
                self.cleaned_data['lng'] is None or self.cleaned_data['lat'] is None):
            raise forms.ValidationError(_('We need your location to generate a random tour, please try again.'))
        return self.cleaned_data


class NotValidatedMultipleChoiceField(TypedMultipleChoiceField):
    def to_python(self, value):
        return map(self.coerce, value)

    def validate(self, value):
        pass


class OrderedTourForm(forms.Form):
    ids = NotValidatedMultipleChoiceField(coerce=str, required=False)


class TourSelectionForm(forms.Form):
    tour = forms.ModelChoiceField(queryset=Tour.objects.all())


class TourGroupSelectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.tour = kwargs.pop('tour', None)
        self.profile = kwargs.pop('profile', None)
        super(TourGroupSelectionForm, self).__init__(*args, **kwargs)
        self.fields['group'].queryset = TourGroup.objects.annotate(member_count=Count('members')) \
            .filter(tour=self.tour, max_members__gt=F('member_count'))

    def clean(self):
        super(TourGroupSelectionForm, self).clean()
        current_member_count = self.cleaned_data['group'].members.count()
        user_current_group = self.profile.tour_groups.filter(tour=self.tour).first()
        if current_member_count >= self.cleaned_data['group'].max_members:
            raise forms.ValidationError(_('This group is full'))
        elif user_current_group:
            raise forms.ValidationError(_("You're already in group %(group)s") % {'group': user_current_group.name})
        else:
            return self.cleaned_data

    group = forms.ModelChoiceField(queryset=TourGroup.objects.all(), label=_('Group'))


class MapMarkersForm(forms.Form):
    lat = forms.FloatField(min_value=-85.05115, max_value=85)
    lng = forms.FloatField(min_value=-180, max_value=180)


class UserRegistrationForm(RegistrationFormUniqueEmail):
    username = forms.CharField(max_length=254, required=False, widget=forms.HiddenInput())
    first_name = forms.CharField(label=_('First name'), max_length=30)
    last_name = forms.CharField(label=_('Last name'), max_length=30)

    def clean_email(self):
        email = self.cleaned_data['email']
        self.cleaned_data['username'] = email
        return email


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('send_then_and_now_photos_to_ajapaik',)
        labels = {
            'send_then_and_now_photos_to_ajapaik': _('Upload rephotos to Ajapaik')
        }


class TourEditForm(autocomplete_light.ModelForm):
    class Meta:
        model = Tour
        fields = ('photo_set_type', 'photos', 'grouped')
        labels = {
            'photo_set_type': _('Photo set type'),
            'photos': _('Photos'),
            'grouped': _('With groups')
        }


class TourGroupInlineForm(autocomplete_light.ModelForm):
    class Meta:
        model = TourGroup
        exclude = ('members',)
        labels = {
            'name': _('Group name'),
            'max_members': _('Maximum number of members'),
            'grouped': _('With groups')
        }


TourGroupFormset = inlineformset_factory(Tour, TourGroup, form=TourGroupInlineForm, extra=1)


# Signals
def user_created(sender, user, request, **kwargs):
    form = UserRegistrationForm(request.POST)
    user = User.objects.filter(username=form.data['email']).first()
    if user:
        user.first_name = form.data['first_name']
        user.last_name = form.data['last_name']
        user.save()


user_registered.connect(user_created)


# User checks
def user_has_confirmed_email(user):
    ok = True
    if not hasattr(user, 'email'):
        ok = False
    else:
        if not user.email:
            ok = False
    return ok and user.is_active


# Serializers
class MapPhotoSerializer(serializers.ModelSerializer):
    permaURL = serializers.SerializerMethodField('get_permalink')
    imageURL = serializers.SerializerMethodField('get_image_url')
    order = serializers.SerializerMethodField('get_tour_photo_order')
    usersCompleted = serializers.SerializerMethodField('get_completed_users')
    groupsCompleted = serializers.SerializerMethodField('get_completed_groups')

    def __init__(self, *args, **kwargs):
        self.tour = kwargs.pop('tour', None)
        self.completion_data = kwargs.pop('completion_data', None)
        self.tour_photo_order = kwargs.pop('tour_photo_order', None)
        super(MapPhotoSerializer, self).__init__(**kwargs)

    def get_permalink(self, obj):
        return self.context['request'].build_absolute_uri(
                reverse('project.ajapaik.then_and_now_tours.detail', args=(self.tour.pk, obj.pk)))

    def get_image_url(self, obj):
        return self.context['request'].build_absolute_uri(
                reverse('project.ajapaik.views.image_thumb', args=(obj.pk, 50, obj.get_pseudo_slug())))

    def get_tour_photo_order(self, obj):
        if obj.pk in self.tour_photo_order:
            return self.tour_photo_order.index(obj.pk)
        return None

    def get_completed_users(self, obj):
        if obj.pk in self.completion_data:
            return self.completion_data[obj.pk]['users']
        return None

    def get_completed_groups(self, obj):
        if obj.pk in self.completion_data:
            return self.completion_data[obj.pk]['groups']
        return None

    class Meta:
        model = Photo
        fields = ('description', 'lat', 'lon', 'order', 'permaURL', 'imageURL', 'usersCompleted', 'groupsCompleted')


class GalleryPhotoSerializer(serializers.ModelSerializer):
    permaURL = serializers.SerializerMethodField('get_permalink')
    imageURL = serializers.SerializerMethodField('get_image_url')
    usersCompleted = serializers.SerializerMethodField('get_completed_users')
    groupsCompleted = serializers.SerializerMethodField('get_completed_groups')

    def __init__(self, *args, **kwargs):
        self.tour = kwargs.pop('tour', None)
        self.completion_data = kwargs.pop('completion_data', None)
        self.tour_photo_order = kwargs.pop('tour_photo_order', None)
        super(GalleryPhotoSerializer, self).__init__(**kwargs)

    def get_permalink(self, obj):
        return self.context['request'].build_absolute_uri(
                reverse('project.ajapaik.then_and_now_tours.detail', args=(self.tour.pk, obj.pk)))

    def get_image_url(self, obj):
        return self.context['request'].build_absolute_uri(
                reverse('project.ajapaik.views.image_thumb', args=(obj.pk, 50, obj.get_pseudo_slug())))

    def get_completed_users(self, obj):
        if obj.pk in self.completion_data:
            return self.completion_data[obj.pk]['users']
        return None

    def get_completed_groups(self, obj):
        if obj.pk in self.completion_data:
            return self.completion_data[obj.pk]['groups']
        return None

    class Meta:
        model = Photo
        fields = ('description', 'permaURL', 'imageURL', 'usersCompleted', 'groupsCompleted')


# Views
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
def generate_ordered_tour(request):
    profile = request.user.profile
    form = OrderedTourForm(request.POST)
    if form.is_valid():
        tour = Tour(
                name=_('Fixed tour'),
                user=profile,
                ordered=True,
                photo_set_type=Tour.FIXED
        )
        tour.save()
        i = 0
        for each in Photo.objects.filter(pk__in=form.cleaned_data['ids'], lat__isnull=False, lon__isnull=False).all():
            tour.photos.add(each)
            TourPhotoOrder(
                    photo=each,
                    tour=tour,
                    order=i
            ).save()
            i += 1
        return HttpResponse(json.dumps({'tour': tour.pk}), content_type='application/json')

    return HttpResponse(json.dumps({}), content_type='application/json')


@user_passes_test(user_has_confirmed_email, login_url='/accounts/login/')
def map_view(request, tour_id=None):
    if tour_id is None:
        return redirect(reverse('project.ajapaik.then_and_now_tours.frontpage'))
    tour = get_object_or_404(Tour, id=tour_id)
    profile = request.user.profile
    user_has_group = TourGroup.objects.filter(tour=tour, members__pk=profile.user_id).exists()
    if tour.grouped and not user_has_group:
        return redirect(reverse('project.ajapaik.then_and_now_tours.choose_group', args=(tour.pk,)))
    ret = {
        'tour': tour,
        'is_map': True
    }

    return render_to_response('then_and_now/map.html', RequestContext(request, ret))


@user_passes_test(user_has_confirmed_email, login_url='/accounts/login/')
def get_map_markers(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    form = MapMarkersForm(request.GET)
    photos = tour.photos.all()
    if tour.photo_set_type == tour.ANY:
        if form.is_valid():
            user_location = Point(form.cleaned_data['lng'], form.cleaned_data['lat'])
            photos = Photo.objects.filter(
                    rephoto_of__isnull=True,
                    geography__distance_lte=(user_location, D(m=THEN_AND_NOW_TOUR_RANDOM_PHOTO_MAX_DIST)),
                    geography__distance_gte=(user_location, D(m=THEN_AND_NOW_TOUR_RANDOM_PHOTO_MIN_DIST)),
            )
    tour_photo_order = list(
        TourPhotoOrder.objects.filter(tour=tour).order_by('-order').values_list('photo_id', flat=True))
    completion_data = TourRephoto.objects.filter(tour=tour).values('original', 'user', 'user__tour_groups')
    completion_dict = {}
    for each in completion_data:
        if each['original'] not in completion_dict:
            completion_dict[each['original']] = {'users': [], 'groups': []}
        if each['user'] and each['user'] not in completion_dict[each['original']]['users']:
            completion_dict[each['original']]['users'].append(each['user'])
        if each['user__tour_groups'] \
                and each['user__tour_groups'] not in completion_dict[each['original']]['groups']:
            completion_dict[each['original']]['groups'].append(each['user__tour_groups'])
    serializer = MapPhotoSerializer(photos, context={'request': request}, tour=tour, many=True,
                                    tour_photo_order=tour_photo_order, completion_data=completion_dict)
    markers = serializer.data

    return HttpResponse(JSONRenderer().render(markers), content_type='application/json')


@user_passes_test(user_has_confirmed_email, login_url='/accounts/login/')
def get_gallery_photos(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    form = MapMarkersForm(request.GET)
    photos = tour.photos.all()
    if tour.photo_set_type == tour.ANY:
        if form.is_valid():
            user_location = Point(form.cleaned_data['lng'], form.cleaned_data['lat'])
            photos = Photo.objects.filter(
                    rephoto_of__isnull=True,
                    geography__distance_lte=(user_location, D(m=THEN_AND_NOW_TOUR_RANDOM_PHOTO_MAX_DIST)),
                    geography__distance_gte=(user_location, D(m=THEN_AND_NOW_TOUR_RANDOM_PHOTO_MIN_DIST)),
            )
    tour_photo_order = list(
        TourPhotoOrder.objects.filter(tour=tour).order_by('-order').values_list('photo_id', flat=True))
    completion_data = TourRephoto.objects.filter(tour=tour).values('original', 'user', 'user__tour_groups')
    completion_dict = {}
    for each in completion_data:
        if each['original'] not in completion_dict:
            completion_dict[each['original']] = {'users': [], 'groups': []}
        if each['user'] and each['user'] not in completion_dict[each['original']]['users']:
            completion_dict[each['original']]['users'].append(each['user'])
        if each['user__tour_groups'] \
                and each['user__tour_groups'] not in completion_dict[each['original']]['groups']:
            completion_dict[each['original']]['groups'].append(each['user__tour_groups'])
    serializer = GalleryPhotoSerializer(photos, context={'request': request}, tour=tour, many=True,
                                        tour_photo_order=tour_photo_order, completion_data=completion_dict)
    markers = serializer.data

    return HttpResponse(JSONRenderer().render(markers), content_type='application/json')


@user_passes_test(user_has_confirmed_email, login_url='/accounts/login/')
def choose_group(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    profile = request.user.profile
    form = TourGroupSelectionForm(tour=tour, profile=profile)
    if request.method == 'POST':
        form = TourGroupSelectionForm(request.POST, tour=tour, profile=profile)
        if form.is_valid():
            form.cleaned_data['group'].members.add(profile)
            return redirect(reverse('project.ajapaik.then_and_now_tours.map_view', args=(tour.pk,)))

    return render_to_response('then_and_now/choose_group.html', RequestContext(request, {'form': form}))


@user_passes_test(user_has_confirmed_email, login_url='/accounts/login/')
def gallery(request, tour_id):
    ret = {
        'is_gallery': True
    }
    tour = Tour.objects.filter(pk=tour_id).first()
    profile = request.user.profile
    if tour:
        ret['tour'] = tour
        photos = tour.photos.order_by('tourphoto__order').annotate(rephoto_count=Count('tour_rephotos'))
        rephoto_authors = photos.values_list('tour_rephotos__user', 'tour_rephotos__original')
        rephoto_author_dict = {}
        for each in rephoto_authors:
            author_id = each[0]
            original_id = each[1]
            if author_id is not None and original_id is not None:
                if author_id in rephoto_author_dict:
                    rephoto_author_dict[author_id].append(original_id)
                else:
                    rephoto_author_dict[author_id] = [original_id]
        for each in photos:
            each.user_has_rephotographed = profile.user_id in rephoto_author_dict and each.id in rephoto_author_dict[
                profile.user_id]
        ret['photos'] = photos

    return render_to_response('then_and_now/gallery.html', RequestContext(request, ret))


@user_passes_test(user_has_confirmed_email, login_url='/accounts/login/')
def detail(request, tour_id, photo_id, rephoto_id=None):
    photo = get_object_or_404(Photo, id=photo_id)
    tour = get_object_or_404(Tour, id=tour_id)
    rp = None
    if rephoto_id:
        rp = get_object_or_404(TourRephoto, id=rephoto_id)
    profile = request.user.profile
    current_photo_index = None
    current_rephoto_index = None
    tour_photo_order = list(
        TourPhotoOrder.objects.filter(tour=tour).order_by('order').values_list('photo_id', flat=True))
    rephoto_order = list(
            TourRephoto.objects.filter(tour=tour, original=photo).order_by('created').values_list('id', flat=True))
    if photo.id in tour_photo_order:
        current_photo_index = tour_photo_order.index(photo.id)
    ret = {
        'photo': photo,
        'rephoto': rp,
        'tour': tour,
        'rephotos': TourRephoto.objects.filter(original=photo, tour=tour),
        'is_detail': True
    }
    if tour.grouped:
        photo_captured_by_groups = TourRephoto.objects.filter(tour=tour, original=photo,
                                                              user__tour_groups__isnull=False) \
            .values_list('user__tour_groups', flat=True).distinct('user__tour_groups')
        user_current_group = profile.tour_groups.filter(tour=tour).first()
        if photo_captured_by_groups:
            photo_captured_by_group = TourGroup.objects.get(pk=photo_captured_by_groups[0])
            ret['photo_captured_by_group'] = photo_captured_by_group
            if user_current_group == photo_captured_by_group:
                ret['current_user_group_captured'] = True
            else:
                ret['current_user_group_captured'] = False
    ret['current_user_captured'] = TourRephoto.objects.filter(tour=tour, original=photo, user=profile).exists()
    if (current_photo_index and len(tour_photo_order) - 1) > current_photo_index:
        ret['next_photo'] = Photo.objects.filter(id=tour_photo_order[current_photo_index + 1]).first()
    if current_photo_index > 0:
        ret['previous_photo'] = Photo.objects.filter(id=tour_photo_order[current_photo_index - 1]).first()
    if rp:
        if rp.id in rephoto_order:
            current_rephoto_index = rephoto_order.index(rp.id)
        if (current_rephoto_index and len(rephoto_order) - 1) > current_rephoto_index:
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
    profile = request.user.profile
    form = CameraUploadForm(request.POST, request.FILES)
    if form.is_valid():
        tour = form.cleaned_data['tour']
        TourRephoto(
                image=form.cleaned_data['image'],
                original=form.cleaned_data['original'],
                tour=tour,
                user=profile
        ).save()
        if profile.send_then_and_now_photos_to_ajapaik:
            now = datetime.datetime.now()
            Photo(
                    image=form.cleaned_data['image'],
                    is_then_and_now_rephoto=True,
                    user=profile,
                    description=form.cleaned_data['original'].description,
                    licence=Licence.objects.filter(name='Attribution-ShareAlike 4.0 International').first(),
                    rephoto_of=form.cleaned_data['original'],
                    date=now
            ).save()
            form.cleaned_data['original'].latest_rephoto = now
            form.cleaned_data['original'].light_save()
        each_photo_done = True
        if tour.photo_set_type == tour.FIXED:
            for each in tour.photos.all():
                if not TourRephoto.objects.filter(tour=tour, original=each, user=profile).exists():
                    each_photo_done = False
                    break
            if each_photo_done:
                return redirect(reverse('project.ajapaik.then_and_now_tours.tour_complete', args=(tour.pk,)))
        return redirect(reverse('project.ajapaik.then_and_now_tours.map_view', args=(tour.pk,)))

    return HttpResponse(ret)


@user_passes_test(user_has_confirmed_email, login_url='/accounts/login/')
def tour_complete(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    ret = {
        'tour': tour,
        'minutes': (datetime.datetime.utcnow().replace(tzinfo=utc) - tour.created.replace(tzinfo=utc)).seconds / 60
    }

    return render_to_response('then_and_now/tour_complete.html', RequestContext(request, ret))


@user_passes_test(user_has_confirmed_email, login_url='/accounts/login/')
def participants(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    rephoto_authors = tour.tour_rephotos.values('user').annotate(rephoto_count=Count('pk')).order_by('-rephoto_count')
    users = User.objects.filter(id__in=[x['user'] for x in rephoto_authors])
    users_dict = {x.id: x for x in users}
    for each in rephoto_authors:
        each['user'] = users_dict[each['user']]
    ret = {
        'is_participants': True,
        'participants': rephoto_authors,
        'tour': tour
    }
    return render_to_response('then_and_now/participants.html', RequestContext(request, ret))


@user_passes_test(user_has_confirmed_email, login_url='/accounts/login/')
def manage(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    if request.method == 'POST':
        form = TourEditForm(request.POST, instance=tour)
        group_formset = TourGroupFormset(request.POST, instance=tour)
        if group_formset.is_valid() and form.is_valid():
            form.save()
            group_formset.save()
    else:
        form = TourEditForm(instance=tour)
        group_formset = TourGroupFormset(instance=tour)
    ret = {
        'form': form,
        'group_formset': group_formset,
        'tour': tour,
        'is_tour_manager': True
    }
    return render_to_response('then_and_now/manage.html', RequestContext(request, ret))


@user_passes_test(user_has_confirmed_email, login_url='/accounts/login/')
def settings(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=profile)
        form.save()
    else:
        form = ProfileEditForm(instance=profile)
    ret = {
        'form': form,
        'is_settings': True,
        'tour': tour
    }

    return render_to_response('then_and_now/settings.html', RequestContext(request, ret))


@user_passes_test(user_has_confirmed_email, login_url='/accounts/login/')
def choose_new_tour_type(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ChooseNewTourTypeForm(request.POST)
        if form.is_valid():
            t = form.cleaned_data['tour_type']
            if t == form.NEARBY_RANDOM:
                generation_form = RandomTourForm(request.POST)
                if generation_form.is_valid():
                    user_lat = generation_form.cleaned_data['lat']
                    user_lng = generation_form.cleaned_data['lng']
                    max_dist = generation_form.cleaned_data['max_distance']
                    min_dist = generation_form.cleaned_data['min_distance']
                    how_many = generation_form.cleaned_data['random_count']
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
                            user=profile,
                            photo_set_type=Tour.FIXED
                    )
                    tour.save()
                    for each in sample:
                        tour.photos.add(each)

                    return redirect(reverse('project.ajapaik.then_and_now_tours.map_view', args=(tour.pk,)))
                else:
                    return redirect(reverse('project.ajapaik.then_and_now_tours.frontpage'))
            elif t == form.FIXED:
                tour = Tour(
                        name=_('Fixed tour'),
                        user=profile,
                        photo_set_type=Tour.FIXED
                )
                tour.save()
                return redirect(reverse('project.ajapaik.then_and_now_tours.manage', args=(tour.pk,)))
            elif t == form.OPEN:
                tour = Tour(
                        name=_('Open tour'),
                        user=profile,
                        photo_set_type=Tour.ANY
                )
                tour.save()
                return redirect(reverse('project.ajapaik.then_and_now_tours.map_view', args=(tour.pk,)))
    else:
        form = ChooseNewTourTypeForm(
            initial={'lat': request.GET.get('lat') or None, 'lng': request.GET.get('lng') or None})
    ret = {
        'form': form
    }

    return render_to_response('then_and_now/choose_new_tour_type.html', RequestContext(request, ret))
