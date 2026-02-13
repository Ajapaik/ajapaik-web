from ajapaik.ajapaik.forms import AddAlbumForm, AreaSelectionForm, AlbumSelectionForm, AddAreaForm, \
    GameAlbumSelectionForm, GameNextPhotoForm, MapDataRequestForm, GalleryFilteringForm, \
    PhotoSelectionForm, SelectionUploadForm, AlbumInfoModalForm, PhotoLikeForm, \
    AlbumSelectionFilteringForm, CuratorWholeSetAlbumsSelectionForm
from django.db.models import Sum, Q, Count, F, Min, Max
import json
from sorl.thumbnail import get_thumbnail
from django.shortcuts import redirect, get_object_or_404, render
from django.core.management.base import BaseCommand
from django.conf import settings
#from ajapaik.ajapaik_profile.models import Photo
import time
from django.test.client import RequestFactory
from ajapaik.ajapaik.models import Profile, Photo, GeoTag, Album, AlbumPhoto, PhotoLike, ImageSimilarity, Licence
from ajapaik.ajapaik.utils import get_pagination_parameters, is_ajax
from ajapaik.ajapaik.serializers import FrontpageAlbumSerializer, DatingSerializer, \
    VideoSerializer, PhotoMapMarkerSerializer
from rest_framework.renderers import JSONRenderer
from django.urls import reverse

start_time = time.time()

def _make_fullscreen(p):
    if p and p.image:
        return {'url': p.image.url, 'size': [p.image.width, p.image.height]}

def print_time_diff(msg):
    global start_time
    if start_time:
        print(msg + ": " + str(time.time() - start_time))

    start_time=time.time()


def test_photoslug(request=None, photo_id=None, profile=None):
    print_time_diff("Pre")

    is_frontpage = False
    is_mapview = False
    is_selection = False
    rephoto_fullscreen = None
    similar_fullscreen = None
    title = 'none'
    whole_set_albums_selection_form = CuratorWholeSetAlbumsSelectionForm()

    print_time_diff("Alku")

#    profile = request.get_user().profile
    photo_obj = get_object_or_404(Photo, id=photo_id)

    print_time_diff("A")
    user_has_likes = profile.likes.exists()
    user_has_rephotos = profile.photos.filter(rephoto_of__isnull=False).exists()
    print_time_diff("B")

    user_has_likes = profile.likes.exists()
    user_has_rephotos = profile.photos.filter(rephoto_of__isnull=False).exists()

    print_time_diff("C")

    # switch places if rephoto url
    rephoto = None
    first_rephoto = None
    if hasattr(photo_obj, 'rephoto_of') and photo_obj.rephoto_of is not None:
        rephoto = photo_obj
        photo_obj = photo_obj.rephoto_of

    print_time_diff("D")

    geotag_count = 0
    azimuth_count = 0
    original_thumb_size = None
    first_geotaggers = []
    if photo_obj:
        original_thumb_size = get_thumbnail(photo_obj.image, '1024x1024').size
        geotags = GeoTag.objects.filter(photo_id=photo_obj.id).distinct('user_id').order_by('user_id', '-created')
        geotag_count = geotags.count()
        if geotag_count > 0:
            correct_geotags_from_authenticated_users = geotags.exclude(user__pk=profile.user_id).filter(
                Q(user__first_name__isnull=False, user__last_name__isnull=False, is_correct=True))[:3]
            if correct_geotags_from_authenticated_users.exists():
                for each in correct_geotags_from_authenticated_users:
                    first_geotaggers.append([each.user.get_display_name, each.lat, each.lon, each.azimuth])
            first_geotaggers = json.dumps(first_geotaggers)
        azimuth_count = geotags.filter(azimuth__isnull=False).count()
        first_rephoto = photo_obj.rephotos.all().first()

    print_time_diff("E")

    album_ids = AlbumPhoto.objects.filter(photo_id=photo_obj.id).values_list('album_id', flat=True)
    full_album_id_list = list(album_ids)
    albums = Album.objects.filter(pk__in=album_ids, atype=Album.CURATED).prefetch_related('subalbum_of')
    collection_albums = Album.objects.filter(pk__in=album_ids, atype=Album.COLLECTION)
    for each in albums:
        if each.subalbum_of:
            current_parent = each.subalbum_of
            while current_parent is not None:
                full_album_id_list.append(current_parent.id)
                current_parent = current_parent.subalbum_of
    albums = Album.objects.filter(pk__in=full_album_id_list, atype=Album.CURATED)
    for a in albums:
        first_albumphoto = AlbumPhoto.objects.filter(photo_id=photo_obj.id, album=a).first()
        if first_albumphoto:
            a.this_photo_curator = first_albumphoto.profile
    album = albums.first()
    next_photo = None
    previous_photo = None

    print_time_diff("F")

    if album:
        album_selection_form = AlbumSelectionForm({'album': album.id})
        if not is_ajax(request):
            next_photo_id = \
                AlbumPhoto.objects.filter(photo_id__gt=photo_obj.pk, album=album.id).aggregate(min_id=Min('photo_id'))[
                    'min_id']
            if next_photo_id:
                # AlbumPhotos can return something which is filtered out by our custom manager, don't use .get() here.
                next_photo = Photo.objects.filter(pk=next_photo_id).first()

            previous_photo_id = \
                AlbumPhoto.objects.filter(photo_id__lt=photo_obj.pk, album=album.id).aggregate(max_id=Max('photo_id'))[
                    'max_id']
            if previous_photo_id:
                # AlbumPhotos can return something which is filtered out by our custom manager, don't use .get() here.
                previous_photo = Photo.objects.filter(pk=previous_photo_id).first()
    else:
        album_selection_form = AlbumSelectionForm(
            initial={'album': Album.objects.filter(is_public=True).order_by('-created').first()}
        )
        if not is_ajax(request):
            next_photo_id = Photo.objects.filter(pk__gt=photo_obj.pk).aggregate(min_id=Min('id'))['min_id']
            if next_photo_id:
                # AlbumPhotos can return something which is filtered out by our custom manager, don't use .get() here.
                next_photo = Photo.objects.filter(pk=next_photo_id).first()

            previous_photo_id = Photo.objects.filter(pk__lt=photo_obj.pk).aggregate(max_id=Max('id'))['max_id']
            if previous_photo_id:
                # AlbumPhotos can return something which is filtered out by our custom manager, don't use .get() here.
                previous_photo = Photo.objects.filter(pk=previous_photo_id).first()

    if album:
        album = (album.id, album.lat, album.lon)

    print_time_diff("G")


    if photo_obj and photo_obj.get_display_text:
        photo_obj.tags = ','.join(photo_obj.get_display_text.split(' '))
    if rephoto and rephoto.get_display_text:
        rephoto.tags = ','.join(rephoto.get_display_text.split(' '))

    print_time_diff("H")

    user_confirmed_this_location = 'false'
    user_has_geotagged = GeoTag.objects.filter(photo=photo_obj, user=profile).exists()
    if user_has_geotagged:
        user_has_geotagged = 'true'
    else:
        user_has_geotagged = 'false'
    last_user_confirm_geotag_for_this_photo = GeoTag.objects.filter(type=GeoTag.CONFIRMATION, photo=photo_obj,
                                                                    user=profile) \
        .order_by('-created').first()
    if last_user_confirm_geotag_for_this_photo:
        if last_user_confirm_geotag_for_this_photo.lat == photo_obj.lat \
                and last_user_confirm_geotag_for_this_photo.lon == photo_obj.lon:
            user_confirmed_this_location = 'true'

    print_time_diff("I")

    likes = PhotoLike.objects.filter(photo=photo_obj)
    photo_obj.like_count = likes.distinct('profile').count()
    like = likes.filter(profile=profile).first()
    if like:
        if like.level == 1:
            photo_obj.user_likes = True
        elif like.level == 2:
            photo_obj.user_loves = True

    print_time_diff("J")

    previous_datings = photo_obj.datings.order_by('created').prefetch_related('confirmations')
    for each in previous_datings:
        each.this_user_has_confirmed = each.confirmations.filter(profile=profile).exists()
    serialized_datings = DatingSerializer(previous_datings, many=True).data
    serialized_datings = JSONRenderer().render(serialized_datings).decode('utf-8')

    print_time_diff("K")

    strings = []
    if photo_obj.source:
        strings = [photo_obj.source.description, photo_obj.source_key]
    desc = ' '.join(filter(None, strings))

    next_similar_photo = photo_obj
    if next_photo is not None:
        next_similar_photo = next_photo
    compare_photos_url = request.build_absolute_uri(
        reverse('compare-photos', args=(photo_obj.id, next_similar_photo.id)))
    image_similarities = ImageSimilarity.objects.filter(from_photo_id=photo_obj.id).exclude(similarity_type=0)
    if image_similarities.exists():
        compare_photos_url = request.build_absolute_uri(
            reverse('compare-photos', args=(photo_obj.id, image_similarities.first().to_photo_id)))

    people = [x.name for x in photo_obj.people]
    similar_photos = ImageSimilarity.objects.filter(from_photo=photo_obj.id).exclude(similarity_type=0)

    print_time_diff("L")

    reverse_side = None
    if photo_obj.back_of is not None:
        reverse_side = photo_obj.back_of
    elif photo_obj.front_of is not None:
        reverse_side = photo_obj.front_of

    seconds = None
    if photo_obj.video_timestamp:
        seconds = photo_obj.video_timestamp / 1000

    print_time_diff("M")

    context = {
        'photo': photo_obj,
        'similar_photos': similar_photos,
        'previous_datings': serialized_datings,
        'datings_count': previous_datings.count(),
        'original_thumb_size': original_thumb_size,
        'user_confirmed_this_location': user_confirmed_this_location,
        'user_has_geotagged': user_has_geotagged,
        'fb_url': request.build_absolute_uri(reverse('photo', args=(photo_obj.id,))),
        'licence': Licence.objects.get(id=17),  # CC BY 4.0
        'area': photo_obj.area,
        'album': album,
        'albums': albums,
        'collection_albums': collection_albums,
        'is_frontpage': is_frontpage,
        'is_mapview': is_mapview,
        'is_selection': is_selection,
        'album_selection_form': album_selection_form,
        'geotag_count': geotag_count,
        'azimuth_count': azimuth_count,
        'fullscreen': _make_fullscreen(photo_obj),
        'rephoto_fullscreen': rephoto_fullscreen,
        'similar_fullscreen': similar_fullscreen,
        'title': title,
        'description': desc,
        'rephoto': rephoto,
        'hostname': request.build_absolute_uri('/'),
        'first_geotaggers': first_geotaggers,
        'is_photoview': True,
        'ajapaik_facebook_link': settings.AJAPAIK_FACEBOOK_LINK,
        'user_has_likes': user_has_likes,
        'user_has_rephotos': user_has_rephotos,
        'next_photo': next_photo,
        'previous_photo': previous_photo,
        'similar_photo_count': similar_photos.count(),
        'confirmed_similar_photo_count': similar_photos.filter(confirmed=True).count(),
        'compare_photos_url': compare_photos_url,
	'reverse_side': reverse_side,
        'is_photo_modal': is_ajax(request),
        # TODO: Needs more data than just the names
        'people': people,
        'whole_set_albums_selection_form': whole_set_albums_selection_form,
        'seconds': seconds
    }

    print_time_diff("N")


class Command(BaseCommand):
    help = 'Test photoslug (2024)'

    def handle(self, *args, **options):
        profile = Profile.objects.get(pk=44387121)
        rf = RequestFactory()
        request= rf.get('/photo/124147/saaremaa-sorve-fire-tower/')

        profile = Profile.objects.get(pk=38)
        test_photoslug(request, 124147, profile)

        print("OK")
