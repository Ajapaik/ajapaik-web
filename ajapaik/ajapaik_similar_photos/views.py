from django.conf import settings
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from ajapaik.ajapaik.models import ImageSimilarity, ImageSimilaritySuggestion, Photo
from ajapaik.ajapaik.serializers import PhotoDetailsSerializer


def compare_all_photos(request, photo_id=None, photo_id_2=None):
    return compare_photos_generic(request, photo_id, photo_id_2, 'compare-all-photos', True)


def compare_photos(request, photo_id=None, photo_id_2=None):
    return compare_photos_generic(request, photo_id, photo_id_2)


def compare_photos_generic(request, photo_id=None, photo_id_2=None, view='compare-photos', compare_all=False):
    profile = request.get_user().profile
    similar_photos = None
    if not photo_id or not photo_id_2:
        first_similar = ImageSimilarity.objects.filter(confirmed=False).first()
        if first_similar is None:
            suggestions = ImageSimilaritySuggestion.objects.filter(proposer_id=profile.id) \
                .order_by('proposer_id', '-created').all().values_list('image_similarity_id', flat=True)
            if suggestions is None:
                similar_photos = ImageSimilarity.objects.all()
            else:
                similar_photos = ImageSimilarity.objects.exclude(id__in=suggestions)
            if similar_photos is None or len(similar_photos) < 1:
                return render(request, 'compare_photos/compare_photos_no_results.html')
            first_similar = similar_photos.first()
        photo_id = first_similar.from_photo_id
        photo_id_2 = first_similar.to_photo_id

    photo_obj = get_object_or_404(Photo, id=photo_id)
    photo_obj2 = get_object_or_404(Photo, id=photo_id_2)

    first_photo_criterion = Q(from_photo=photo_obj) & Q(to_photo=photo_obj2)
    second_photo_criterion = Q(from_photo=photo_obj2) & Q(to_photo=photo_obj)
    master_criterion = Q(first_photo_criterion | second_photo_criterion)
    if similar_photos is None or len(similar_photos) < 1:
        similar_photos = ImageSimilarity.objects.exclude(master_criterion | Q(confirmed=True))
        first_photo = similar_photos.filter(Q(from_photo=photo_obj) & Q(confirmed=False)).first()
        second_photo = similar_photos.filter(Q(from_photo=photo_obj2) & Q(confirmed=False)).first()
    else:
        first_photo = similar_photos.filter(from_photo=photo_obj).first()
        second_photo = similar_photos.filter(from_photo=photo_obj2).first()

    if first_photo:
        next_pair = first_photo
    elif second_photo:
        next_pair = second_photo
    else:
        if compare_all:
            next_pair = similar_photos.first()
        else:
            next_pair = None

    if not next_pair:
        next_action = request.build_absolute_uri(reverse('photo', args=(photo_obj.id, photo_obj.get_pseudo_slug)))
    else:
        next_action = request.build_absolute_uri(reverse(view, args=(next_pair.from_photo_id, next_pair.to_photo_id)))

    context = {
        'is_compare_photo': True,
        'ajapaik_facebook_link': settings.AJAPAIK_FACEBOOK_LINK,
        'photo': PhotoDetailsSerializer(photo_obj, context={'request': request}).data,
        'photo2': PhotoDetailsSerializer(photo_obj2, context={'request': request}).data,
        'next_action': next_action
    }
    return render(request, 'compare_photos/compare_photos.html', context)
