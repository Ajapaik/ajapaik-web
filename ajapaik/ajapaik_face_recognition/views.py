import json
import logging
from collections import Counter, OrderedDict
from typing import Optional, Iterable

from django.db.models import Count
from django.http import HttpResponse, HttpRequest, QueryDict
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from rest_framework.renderers import JSONRenderer

from ajapaik.ajapaik.models import Album, AlbumPhoto, Points
from ajapaik.ajapaik_face_recognition.domain.face_annotation_feedback_request import FaceAnnotationFeedbackRequest
from ajapaik.ajapaik_face_recognition.domain.face_annotation_remove_request import FaceAnnotationRemoveRequest
from ajapaik.ajapaik_face_recognition.domain.face_annotation_update_request import FaceAnnotationUpdateRequest
from ajapaik.ajapaik_face_recognition.forms import FaceRecognitionSuggestionForm, \
    FaceRecognitionAddPersonForm
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionUserSuggestion, FaceRecognitionRectangle, \
    FaceRecognitionRectangleSubjectDataSuggestion
from ajapaik.ajapaik_face_recognition.service import face_annotation_feedback_service, face_annotation_edit_service, \
    face_annotation_delete_service
from ajapaik.ajapaik_object_recognition import response
from ajapaik.utils import least_frequent

log = logging.getLogger(__name__)


# TODO: These are API endpoint basically - move to api.py and implement with DRF?
def add_subject(request: HttpRequest) -> HttpResponse:
    form = FaceRecognitionAddPersonForm()
    context = {'form': form}
    status = 200
    if request.method == 'POST':
        form = FaceRecognitionAddPersonForm(request.POST.copy())
        context['form'] = form
        if form.is_valid():
            new_album: Album = form.save(commit=False)
            new_album.atype = Album.PERSON
            new_album.is_public = True
            new_album.open = True
            new_album.profile = request.user.profile
            new_album.save()

            status = 201
            context['message'] = new_album.pk
        else:
            status = 400

    return render(request, 'add_subject.html', context, status=status)


def _get_consensus_subject(rectangle: FaceRecognitionRectangle) -> Optional[int]:
    class OrderedCounter(Counter, OrderedDict):
        pass

    suggestions_so_far_for_this_rectangle = FaceRecognitionUserSuggestion.objects.filter(rectangle=rectangle) \
        .distinct('user').order_by('user', '-created').all()
    subject_counts = OrderedCounter(g.subject_album.id for g in suggestions_so_far_for_this_rectangle)
    dict_keys = list(subject_counts)
    if len(dict_keys) == 0:
        return None

    return dict_keys[0]


def save_subject_object(subject_album, rectangle, user_id, user_profile):
    status = 200

    new_suggestion = FaceRecognitionUserSuggestion(
        subject_album=subject_album,
        rectangle=rectangle,
        user_id=user_id,
        origin=FaceRecognitionUserSuggestion.USER
    )
    new_suggestion.save()

    consensus_subject: Optional[int] = _get_consensus_subject(rectangle)
    current_consensus_album = Album.objects.filter(pk=rectangle.subject_consensus_id).first()

    if consensus_subject != rectangle.subject_consensus_id:
        # Consensus was either None or it changed
        if current_consensus_album:
            AlbumPhoto.objects.filter(album=current_consensus_album, photo=rectangle.photo).delete()
        if rectangle.photo not in subject_album.photos.all():
            AlbumPhoto(photo=rectangle.photo, album=subject_album, type=AlbumPhoto.FACE_TAGGED,
                       profile=user_profile).save()
            subject_album.save()
            status = 201

    rectangle.subject_consensus_id = consensus_subject

    points = 75
    Points(
        user=user_profile,
        action=Points.CONFIRM_SUBJECT,
        points=points,
        photo=rectangle.photo,
        subject_confirmation=new_suggestion,
        annotation=rectangle,
        created=timezone.now()
    ).save()

    rectangle.save()

    return {
        'status': status,
        'new_suggestion_id': new_suggestion.id,
        'points': points
    }


def save_subject(form: FaceRecognitionSuggestionForm, user_id, user_profile):
    subject_album: Album = form.cleaned_data['subject_album']
    rectangle: FaceRecognitionRectangle = form.cleaned_data['rectangle']

    return save_subject_object(subject_album, rectangle, user_id, user_profile)


def add_person_rectangle(values, photo, user_id):
    x1 = values['x1']
    x2 = values['x2']
    y1 = values['y1']
    y2 = values['y2']

    # DB stores (top, right, bottom, left)
    coordinates: Iterable[int] = [
        int(float(y1)),
        int(float(x2)),
        int(float(y2)),
        int(float(x1))
    ]
    new_rectangle = FaceRecognitionRectangle(
        photo=photo,
        coordinates=json.dumps(coordinates),
        user_id=user_id,
        origin=FaceRecognitionRectangle.USER
    )
    new_rectangle.save()

    if photo.first_annotation is None:
        photo.first_annotation = new_rectangle.created
    photo.latest_annotation = new_rectangle.created
    photo.annotation_count += 1
    photo.light_save()

    return new_rectangle.id


def add_rectangle_feedback(request, annotation_id):
    face_annotation_feedback_request = FaceAnnotationFeedbackRequest(
        request.user.id,
        annotation_id,
        QueryDict(request.body)
    )
    face_annotation_feedback_service.add_feedback(face_annotation_feedback_request, request)

    return HttpResponse(JSONRenderer().render({'isOk': True}), content_type='application/json', status=200)


def update_annotation(request: HttpRequest, annotation_id: int):
    if request.method != 'PUT':
        return response.not_supported()

    face_annotation_update_request = FaceAnnotationUpdateRequest(
        QueryDict(request.body),
        annotation_id,
        request.user.id
    )

    is_successful = face_annotation_edit_service.update_face_annotation(face_annotation_update_request, request)

    if is_successful:
        return response.success()

    return response.action_failed()


def remove_annotation(request: HttpRequest, annotation_id: int) -> HttpResponse:
    if request.method != 'DELETE':
        return response.not_supported()

    face_annotation_remove_request = FaceAnnotationRemoveRequest(annotation_id, request.user.id)
    has_removed_successfully = face_annotation_delete_service.remove_annotation(face_annotation_remove_request)

    if has_removed_successfully:
        return response.success()

    return response.action_failed()


def get_subject_data_empty(request):
    return render(request, 'add_subject_data_empty.html')


def get_subject_data(request, rectangle_id=None):
    profile = request.get_user().profile
    rectangle = None
    next_rectangle = None
    album_id = request.GET.get('album')
    album_id = album_id and album_id.isdigit() and int(album_id, 10) or None
    unverified_rectangles = FaceRecognitionRectangle.objects.filter(gender=None, deleted=None)
    if album_id:
        albumphoto_ids = AlbumPhoto.objects.filter(album_id=album_id).values_list('photo_id', flat=True)
        unverified_rectangles = unverified_rectangles.filter(photo_id__in=albumphoto_ids)
    if unverified_rectangles.count() > 1:
        rectangles = unverified_rectangles
    else:
        # TODO: If album_id and rectangle_id were specified,
        #       but rectangle_id is not of a photo belonging to album,
        #       then the images will be shown from all suggestions of the user.
        #       It should only show from previous suggestions of the user, which
        #       are of rectangles belonging to photos which are in album with album_id

        suggestions = FaceRecognitionRectangleSubjectDataSuggestion.objects.filter(
            proposer_id=profile.id).all().values_list('face_recognition_rectangle_id', flat=True)
        if suggestions is None:
            rectangles = FaceRecognitionRectangle.objects.filter(deleted=None)
            if album_id:
                rectangles = rectangles.filter(photo_id__in=albumphoto_ids)
        else:
            rectangles = FaceRecognitionRectangle.objects.filter(deleted=None).exclude(id__in=suggestions)
            if album_id:
                rectangles = rectangles.filter(photo_id__in=albumphoto_ids)
            if not rectangles:
                rectangles = FaceRecognitionRectangle.objects.filter(deleted=None).annotate(
                    number_of_suggestions=Count('face_recognition_suggestions')).order_by('-number_of_suggestions')
                if album_id:
                    rectangles = rectangles.filter(photo_id__in=albumphoto_ids)
                suggestion_ids = []
                for suggestion in suggestions:
                    if rectangle_id != str(suggestion):
                        suggestion_ids.append(suggestion)
                rectangles = FaceRecognitionRectangle.objects.filter(deleted=None,
                                                                     id=least_frequent(suggestion_ids)).order_by('?')
                if rectangles is not None:
                    next_rectangle = rectangles.first()
                else:
                    all_rectangles = FaceRecognitionRectangle.objects.filter(deleted=None)
                    if all_rectangles is not None:
                        if album_id is not None:
                            next_rectangle = all_rectangles.filter(photo_id__in=albumphoto_ids).order_by('?').first()
                        else:
                            next_rectangle = all_rectangles.order_by('?').first()
    if rectangle_id and not rectangle:
        rectangle = get_object_or_404(FaceRecognitionRectangle, id=rectangle_id)
    elif not rectangle:
        rectangle = rectangles.order_by('?').first()
    if rectangle is None and album_id:
        rectangle = FaceRecognitionRectangle.objects.filter(photo_id__in=albumphoto_ids).order_by('?').first()
    if not rectangle:
        rectangle = FaceRecognitionRectangle.objects.order_by('?').first()
    if not rectangle:
        return render(request, 'add_subject_data_empty.html')
    if not next_rectangle:
        next_rectangle = rectangles.exclude(id=rectangle.id).order_by('?').first()
    if not next_rectangle:
        if album_id is None:
            next_rectangle = FaceRecognitionRectangle.objects.order_by('?').first()
        else:
            next_rectangle = FaceRecognitionRectangle.objects.filter(photo_id__in=albumphoto_ids).order_by(
                '?').first()
        next_action = request.build_absolute_uri(
            reverse('face_recognition_subject_data', args=(next_rectangle.id,)))
        if next_rectangle and album_id:
            next_action += f'?album={str(album_id)}'
    has_consensus = False
    subject_id = None
    if rectangle and rectangle.subject_consensus:
        has_consensus = True
        subject_id = rectangle.subject_consensus.id
    elif rectangle and rectangle.subject_ai_suggestion:
        has_consensus = True
        subject_id = rectangle.subject_ai_suggestion.id

    context = {
        'rectangle': rectangle,
        'photo': rectangle.photo,
        'coordinates': rectangle.coordinates,
        'next_action': next_action,
        'has_consensus': has_consensus,
        'subject_id': subject_id
    }

    return render(request, 'add_subject_data.html', context)
