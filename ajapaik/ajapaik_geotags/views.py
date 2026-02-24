import json
import operator

from django.conf import settings
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.csrf import ensure_csrf_cookie

from ajapaik.ajapaik.forms import SubmitGeotagForm, ConfirmGeotagForm, AreaSelectionForm, AlbumSelectionForm, \
    GameAlbumSelectionForm, GamePhotoSelectionForm
from ajapaik.ajapaik.models import _calc_trustworthiness, Photo, Points, PhotoFlipSuggestion, GeoTag, Skip, \
    DifficultyFeedback, Album, AlbumPhoto, Area
from ajapaik.ajapaik.serializers import PhotoMiniSerializer
from ajapaik.ajapaik.views import _get_album_choices
from ajapaik.utils import suggest_photo_edit, distance_in_meters, angle_diff


def geotag_add(request):
    submit_geotag_form = SubmitGeotagForm(request.POST)
    profile = request.get_user().profile
    flip_points = 0
    flip_response = ''
    was_flip_successful = None
    context = {}
    if submit_geotag_form.is_valid():
        azimuth_score = 0
        new_geotag = submit_geotag_form.save(commit=False)
        new_geotag.user = profile
        trust = _calc_trustworthiness(profile.id)
        new_geotag.trustworthiness = trust
        tagged_photo = submit_geotag_form.cleaned_data['photo']
        # user flips, photo is flipped -> flip back
        # user flips, photo isn't flipped -> flip
        # user doesn't flip, photo is flipped -> leave flipped
        # user doesn't flip, photo isn't flipped -> leave as is
        if new_geotag.photo_flipped:
            original_photo = Photo.objects.filter(id=tagged_photo.id).first()
            flip_response, flip_suggestions, was_flip_successful, flip_points = suggest_photo_edit(
                [],
                'flip',
                not original_photo.flip,
                Points,
                40,
                Points.FLIP_PHOTO,
                PhotoFlipSuggestion,
                tagged_photo,
                profile,
                flip_response,
                'do_flip'
            )
            PhotoFlipSuggestion.objects.bulk_create(flip_suggestions)
        new_geotag.save()
        initial_lat = tagged_photo.lat
        initial_lon = tagged_photo.lon
        # Calculate new lat, lon, confidence, suggestion_level, azimuth, azimuth_confidence, geotag_count for photo
        tagged_photo.set_calculated_fields()
        tagged_photo.latest_geotag = timezone.now()
        tagged_photo.save()
        processed_tagged_photo = Photo.objects.filter(pk=tagged_photo.id).get()
        context['estimated_location'] = [processed_tagged_photo.lat, processed_tagged_photo.lon]
        if processed_tagged_photo.azimuth:
            context['azimuth'] = processed_tagged_photo.azimuth
        processed_geotag = GeoTag.objects.filter(pk=new_geotag.id).get()
        if processed_geotag.origin == GeoTag.GAME:
            if len(tagged_photo.geotags.all()) == 1:
                score = max(20, int(300 * trust))
            else:
                # TODO: How bulletproof is this? 0 score geotags happen then and again
                try:
                    error_in_meters = distance_in_meters(tagged_photo.lon, tagged_photo.lat, processed_geotag.lon,
                                                         processed_geotag.lat)
                    score = int(130 * max(0, min(1, (1 - (error_in_meters - 15) / float(94 - 15)))))
                except TypeError:
                    score = 0
        else:
            score = int(trust * 100)
        if processed_geotag.hint_used:
            score *= 0.75
        if processed_geotag.azimuth_correct and tagged_photo.azimuth and processed_geotag.azimuth:
            degree_error_point_array = [100, 99, 97, 93, 87, 83, 79, 73, 67, 61, 55, 46, 37, 28, 19, 10]
            difference = int(angle_diff(tagged_photo.azimuth, processed_geotag.azimuth))
            if difference <= 15:
                azimuth_score = degree_error_point_array[int(difference)]
        processed_geotag.azimuth_score = azimuth_score
        processed_geotag.score = score + azimuth_score
        processed_geotag.save()
        context['current_score'] = processed_geotag.score + flip_points
        Points(user=profile, action=Points.GEOTAG, geotag=processed_geotag, points=processed_geotag.score,
               created=timezone.now(), photo=processed_geotag.photo).save()
        geotags_for_this_photo = GeoTag.objects.filter(photo=tagged_photo)
        context['new_geotag_count'] = geotags_for_this_photo.distinct('user').count()
        context['heatmap_points'] = [[x.lat, x.lon] for x in geotags_for_this_photo]
        profile.set_calculated_fields()
        context['feedback_message'] = ''
        processed_photo = Photo.objects.filter(pk=tagged_photo.pk).first()
        if processed_geotag.origin == GeoTag.GAME and processed_photo:
            if processed_photo.lat == initial_lat and processed_photo.lon == initial_lon:
                context['feedback_message'] = _(
                    "Your contribution didn't change the estimated location for the photo, not yet anyway.")
            else:
                context['feedback_message'] = _('The photo has been mapped to a new location thanks to you.')
            if geotags_for_this_photo.count() == 1:
                context['feedback_message'] = _('Your suggestion was first.')
        for a in processed_photo.albums.all():
            qs = a.get_geotagged_historic_photo_queryset_with_subalbums()
            a.geotagged_photo_count_with_subalbums = qs.count()
            a.light_save()
    else:
        if 'lat' not in submit_geotag_form.cleaned_data and 'lon' not in submit_geotag_form.cleaned_data \
                and 'photo_id' in submit_geotag_form.data:
            Skip(user=profile, photo_id=submit_geotag_form.data['photo_id']).save()
            if 'user_skip_array' not in request.session:
                request.session['user_skip_array'] = []
            request.session['user_skip_array'].append(submit_geotag_form.data['photo_id'])
            request.session.modified = True

    context['was_flip_successful'] = was_flip_successful
    context['flip_response'] = flip_response

    return HttpResponse(json.dumps(context), content_type='application/json')


def geotag_confirm(request):
    form = ConfirmGeotagForm(request.POST)
    profile = request.get_user().profile
    context = {
        'message': 'OK'
    }
    if form.is_valid():
        p = form.cleaned_data['photo']
        # Check if user is eligible to confirm location (again)
        last_confirm_geotag_by_this_user_for_p = p.geotags.filter(user_id=profile.id, type=GeoTag.CONFIRMATION) \
            .order_by('-created').first()
        if not last_confirm_geotag_by_this_user_for_p or (p.lat and p.lon and (
                last_confirm_geotag_by_this_user_for_p.lat != p.lat
                and last_confirm_geotag_by_this_user_for_p.lon != p.lon)):
            trust = _calc_trustworthiness(request.get_user().id)
            confirmed_geotag = GeoTag(
                lat=p.lat,
                lon=p.lon,
                origin=GeoTag.MAP_VIEW,
                type=GeoTag.CONFIRMATION,
                map_type=GeoTag.OPEN_STREETMAP,
                hint_used=True,
                user=profile,
                photo=p,
                is_correct=True,
                score=max(1, int(trust * 50)),
                azimuth_score=0,
                trustworthiness=trust
            )
            if p.azimuth:
                confirmed_geotag.azimuth = p.azimuth
                confirmed_geotag.azimuth_correct = True
            confirmed_geotag.save()
            Points(user=profile, action=Points.GEOTAG, geotag=confirmed_geotag, points=confirmed_geotag.score,
                   created=timezone.now(), photo=p).save()
            p.latest_geotag = timezone.now()
            p.save()
            profile.set_calculated_fields()
        context['new_geotag_count'] = GeoTag.objects.filter(photo=p).distinct('user').count()

    return HttpResponse(json.dumps(context), content_type='application/json')


def difficulty_feedback(request):
    user_profile = request.get_user().profile
    # FIXME: Form, better error handling
    if not user_profile:
        return HttpResponse('Error', status=500)
    user_trustworthiness = _calc_trustworthiness(user_profile.pk)
    user_last_geotag = GeoTag.objects.filter(user=user_profile).order_by('-created').first()
    level = request.POST.get('level') or None
    photo_id = request.POST.get('photo_id') or None
    # FIXME: Why so many lines?
    if user_profile and level and photo_id and user_last_geotag:
        feedback_object = DifficultyFeedback()
        feedback_object.user_profile = user_profile
        feedback_object.level = level
        feedback_object.photo_id = photo_id
        feedback_object.trustworthiness = user_trustworthiness
        feedback_object.geotag = user_last_geotag
        feedback_object.save()
        photo = Photo.objects.get(id=photo_id)
        # FIXME: Shouldn't use costly set_calculated_fields here, maybe send extra var to lighten it
        photo.set_calculated_fields()
        photo.save()

    return HttpResponse('OK')


def geotaggers_modal(request, photo_id):
    limit = request.GET.get('limit')
    geotags = GeoTag.objects.filter(photo_id=photo_id).order_by('user', '-created').distinct(
        'user').prefetch_related('user')

    if limit is not None and limit.isdigit():
        geotags = geotags[:int(limit, 10)]

    geotags = sorted(geotags, key=operator.attrgetter('created'), reverse=True)
    geotaggers = []
    if len(geotags) < 1:
        return HttpResponse('No geotags found for image', status=404)
    for geotag in geotags:
        if geotag.user is None:
            if geotag.origin == GeoTag.REPHOTO or geotag.photo.source is None:
                geotaggers.append({'name': _(dict(geotag.ORIGIN_CHOICES)[geotag.origin]), 'created': geotag.created})
            else:
                geotaggers.append({'name': geotag.photo.source.name, 'created': geotag.created})
        else:
            geotaggers.append(
                {'name': geotag.user.get_display_name, 'geotagger_id': geotag.user_id, 'created': geotag.created})
    context = {
        'geotaggers': geotaggers
    }
    return render(request, 'geotaggers/_geotaggers_modal_content.html', context)


@ensure_csrf_cookie
def game(request):
    profile = request.get_user().profile
    user_has_likes = profile.likes.exists()
    user_has_rephotos = profile.photos.filter(rephoto_of__isnull=False).exists()
    area_selection_form = AreaSelectionForm(request.GET)
    album_selection_form = AlbumSelectionForm(
        request.GET,
        initial={'album': Album.objects.filter(is_public=True).order_by('-created').first()}
    )
    game_album_selection_form = GameAlbumSelectionForm(request.GET)
    game_photo_selection_form = GamePhotoSelectionForm(request.GET)
    album = None
    area = None
    context = {
        'albums': _get_album_choices(None, 0, 1)  # Where this is used? Ie. is albums variable used at all
    }

    if game_photo_selection_form.is_valid():
        photo = game_photo_selection_form.cleaned_data['photo']
        context['photo'] = PhotoMiniSerializer(game_photo_selection_form.cleaned_data['photo']).data
        album_ids = AlbumPhoto.objects.filter(photo_id=photo.id).distinct('album_id').values_list('album_id', flat=True)
        album = Album.objects.filter(id__in=album_ids, atype=Album.CURATED).order_by('-created').first()
    elif game_album_selection_form.is_valid():
        album = game_album_selection_form.cleaned_data['album']
    else:
        if area_selection_form.is_valid():
            area = area_selection_form.cleaned_data['area']
        else:
            old_city_id = request.GET.get('city__pk') or None
            if old_city_id is not None:
                area = Area.objects.get(pk=old_city_id)
        context['area'] = area

    facebook_share_photos = []
    if album:
        context['album'] = album
        qs = album.photos.filter(rephoto_of__isnull=True)
        for sa in album.subalbums.exclude(atype=Album.AUTO):
            qs = qs | sa.photos.filter(rephoto_of__isnull=True)
        context['album_photo_count'] = qs.distinct('id').count()
        facebook_share_photos = album.photos.all()[:5]
    elif area:
        facebook_share_photos = Photo.objects.filter(area=area, rephoto_of__isnull=True).order_by('?')[:5]

    context["facebook_share_photos"] = PhotoMiniSerializer(facebook_share_photos, many=True).data

    context['hostname'] = request.build_absolute_uri('/')
    if album:
        context['title'] = album.name
    elif area:
        context['title'] = area.name
    else:
        context['title'] = _('Geotagging game')
    context['is_game'] = True
    context['area_selection_form'] = area_selection_form
    context['album_selection_form'] = album_selection_form
    context['last_geotagged_photo_id'] = Photo.objects.order_by(F('latest_geotag').desc(nulls_last=True)).first().id
    context['ajapaik_facebook_link'] = settings.AJAPAIK_FACEBOOK_LINK
    context['user_has_likes'] = user_has_likes
    context['user_has_rephotos'] = user_has_rephotos

    return render(request, 'common/game.html', context)
