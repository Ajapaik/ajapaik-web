from django.conf import settings
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views.decorators.csrf import ensure_csrf_cookie

from ajapaik.ajapaik.forms import GameAlbumSelectionForm
from ajapaik.ajapaik.gallery_service import get_filtered_data_for_gallery
from ajapaik.ajapaik.models import Photo, GeoTag, Album, AlbumPhoto
from ajapaik.ajapaik.serializers import PhotoMiniSerializer
from ajapaik.ajapaik.views import _get_album_choices
from ajapaik.ajapaik_map.forms import MapDataRequestForm
from ajapaik.ajapaik_map.serializers import PhotoMapMarkerSerializer


@ensure_csrf_cookie
def mapview(request, photo_id=None, rephoto_id=None):
    profile = request.get_user().profile
    game_album_selection_form = GameAlbumSelectionForm(request.GET)
    albums = _get_album_choices(None, 0, 1)  # Where albums variable is used?
    photos_qs = Photo.objects.filter(rephoto_of__isnull=True).values('id')
    select_all_photos = True

    user_has_likes = profile.likes.exists()
    user_has_rephotos = profile.photos.filter(rephoto_of__isnull=False).exists()

    album = None

    if game_album_selection_form.is_valid():
        select_all_photos = False
        album = game_album_selection_form.cleaned_data['album']
        photos_qs = album.photos.prefetch_related('subalbums')
        for sa in album.subalbums.exclude(atype=Album.AUTO):
            photos_qs = photos_qs | sa.photos.filter(rephoto_of__isnull=True)

    selected_photo = None
    selected_rephoto = None
    if rephoto_id:
        selected_rephoto = Photo.objects.filter(pk=rephoto_id).first()

    if photo_id:
        selected_photo = Photo.objects.filter(pk=photo_id).first()
    else:
        if selected_rephoto:
            selected_photo = Photo.objects.filter(pk=selected_rephoto.rephoto_of.id).first()

    if selected_photo and album is None:
        photo_album_ids = AlbumPhoto.objects.filter(photo_id=selected_photo.id).values_list('album_id', flat=True)
        album = Album.objects.filter(pk__in=photo_album_ids, is_public=True).order_by('-created').first()
        if album:
            select_all_photos = False
            photos_qs = album.photos.prefetch_related('subalbums').filter(rephoto_of__isnull=True)
            for sa in album.subalbums.exclude(atype=Album.AUTO):
                photos_qs = photos_qs | sa.photos.filter(rephoto_of__isnull=True)

    # If we are using unfiltered view then we can just count all geotags
    if select_all_photos:
        geotagging_user_count = GeoTag.objects.distinct('user').values('user').count()
        total_photo_count = photos_qs.count()
    else:
        geotagging_user_count = GeoTag.objects.filter(photo_id__in=photos_qs.values_list('id', flat=True)).distinct(
            'user').values('user').count()
        total_photo_count = photos_qs.distinct('id').values('id').count()

    geotagged_photo_count = photos_qs.distinct('id').filter(lat__isnull=False, lon__isnull=False).count()

    if geotagged_photo_count:
        last_geotagged_photo_id = Photo.objects.order_by(F('latest_geotag').desc(nulls_last=True)).values('id').first()[
            'id']
    else:
        last_geotagged_photo_id = None

    context = {'last_geotagged_photo_id': last_geotagged_photo_id,
               'total_photo_count': total_photo_count, 'geotagging_user_count': geotagging_user_count,
               'geotagged_photo_count': geotagged_photo_count, 'albums': albums,
               'hostname': request.build_absolute_uri('/'),
               'selected_photo': selected_photo, 'selected_rephoto': selected_rephoto, 'is_mapview': True,
               'ajapaik_facebook_link': settings.AJAPAIK_FACEBOOK_LINK, 'album': None, 'user_has_likes': user_has_likes,
               'user_has_rephotos': user_has_rephotos, 'q': request.GET.get('q')}

    if album is not None:
        context['album'] = album
        context['title'] = f'{album.name} - {_("Browse photos on map")}'
        context['facebook_share_photos'] = PhotoMiniSerializer(album.photos.all()[:5], many=True).data
    else:
        context['title'] = _('Browse photos on map')

    context['show_photos'] = True
    return render(request, 'common/mapview.html', context)


def map_objects_by_bounding_box(request):
    form = MapDataRequestForm(request.POST)

    if not form.is_valid():
        return JsonResponse({'status': 400})

    profile = request.user.profile
    limit_by_album = form.cleaned_data['limit_by_album']
    sw_lat = form.cleaned_data['sw_lat']
    sw_lon = form.cleaned_data['sw_lon']
    ne_lat = form.cleaned_data['ne_lat']
    ne_lon = form.cleaned_data['ne_lon']
    count_limit = form.cleaned_data['count_limit']

    photo_filters = {
        "lat__gte": sw_lat,
        "lon__gte": sw_lon,
        "lat__lte": ne_lat,
        "lon__lte": ne_lon
    }

    if not limit_by_album and "album" in form.cleaned_data:
        del form.cleaned_data["album"]
        form.cleaned_data["album"] = None

    data = get_filtered_data_for_gallery(profile, cleaned_data=form.cleaned_data, page_size=count_limit or 10000,
                                         photo_filters=photo_filters)

    return JsonResponse({
        'photos': PhotoMapMarkerSerializer(data.photos, many=True,
                                           photo_selection=request.session.get('photo_selection', [])).data
    })
