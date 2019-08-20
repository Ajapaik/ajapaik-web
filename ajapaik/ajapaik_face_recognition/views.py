import json
import logging
from collections import Counter, OrderedDict
from typing import Optional, Iterable

from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import HttpResponse, HttpRequest, QueryDict
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from django.utils import timezone
from rest_framework.renderers import JSONRenderer
from PIL import Image

from ajapaik import settings
from ajapaik.utils import least_frequent
from ajapaik.ajapaik.models import Album, AlbumPhoto, Photo, Points
from ajapaik import settings
from ajapaik.ajapaik_face_recognition.domain.face_annotation_feedback_request import FaceAnnotationFeedbackRequest
from ajapaik.ajapaik_face_recognition.domain.face_annotation_remove_request import FaceAnnotationRemoveRequest
from ajapaik.ajapaik_face_recognition.domain.face_annotation_update_request import FaceAnnotationUpdateRequest
from ajapaik.ajapaik_face_recognition.forms import FaceRecognitionGuessForm, \
    FaceRecognitionRectangleSubmitForm, FaceRecognitionRectangleFeedbackForm, FaceRecognitionAddPersonForm
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionUserGuess, FaceRecognitionRectangle, \
    FaceRecognitionRectangleFeedback, FaceRecognitionRectangleSubjectDataGuess
from ajapaik.ajapaik_face_recognition.serializers import FaceRecognitionRectangleSerializer
from ajapaik.ajapaik_face_recognition.service import face_annotation_feedback_service, face_annotation_edit_service, \
    face_annotation_delete_service
from ajapaik.ajapaik_object_recognition import response

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
            new_album.profile_id = request.user.id
            new_album.save()

            status = 201
            context['message'] = new_album.pk
        else:
            status = 400

    return render(request, 'add_subject.html', context, status=status)


def _get_consensus_subject(rectangle: FaceRecognitionRectangle) -> Optional[int]:
    class OrderedCounter(Counter, OrderedDict):
        pass

    guesses_so_far_for_this_rectangle = FaceRecognitionUserGuess.objects.filter(rectangle=rectangle) \
        .distinct('user').order_by('user', '-created').all()
    subject_counts = OrderedCounter(g.subject_album.id for g in guesses_so_far_for_this_rectangle)
    dict_keys = list(subject_counts)
    if len(dict_keys) == 0:
        return None

    return dict_keys[0]


def save_subject_object(subject_album, rectangle, user_id, user_profile):
    status = 200

    new_guess = FaceRecognitionUserGuess(
        subject_album=subject_album,
        rectangle=rectangle,
        user_id=user_id,
        origin=FaceRecognitionUserGuess.USER
    )
    new_guess.save()

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
        subject_confirmation=new_guess,
        annotation = rectangle,
        created=timezone.now()
    ).save()

    rectangle.save()

    return {
        "status": status,
        "new_guess_id": new_guess.id,
        'points': points
    }


def save_subject(form: FaceRecognitionGuessForm, user_id, user_profile):
    subject_album: Album = form.cleaned_data['subject_album']
    rectangle: FaceRecognitionRectangle = form.cleaned_data['rectangle']

    return save_subject_object(subject_album, rectangle, user_id, user_profile)


def guess_subject(request: HttpRequest) -> HttpResponse:
    status = 200
    if request.method == 'POST':
        form = FaceRecognitionGuessForm(request.POST)
        if form.is_valid():
            result = save_subject(form, request.user.id, request.user.profile)

            status = result["status"]
            new_guess_id = result["new_guess_id"]

            return HttpResponse(JSONRenderer().render({'id': new_guess_id}), content_type='application/json',
                                status=status)

    return HttpResponse('OK', status=status)


def add_rectangle(request: HttpRequest) -> HttpResponse:
    form = FaceRecognitionRectangleSubmitForm(request.POST.copy())
    if form.is_valid():
        photo: Photo = form.cleaned_data['photo']
        width_scale: float = float(form.cleaned_data['seen_width']) / float(photo.width)
        height_scale: float = float(form.cleaned_data['seen_height']) / float(photo.height)
        # jQuery plugin gives x1, y1 topLeft, x2, y2 bottomRight
        # DB stores (top, right, bottom, left)
        coordinates: Iterable[int] = [
            int(float(form.cleaned_data['y1']) / height_scale),
            int(float(form.cleaned_data['x2']) / width_scale),
            int(float(form.cleaned_data['y2']) / height_scale),
            int(float(form.cleaned_data['x1']) / width_scale)
        ]
        new_rectangle = FaceRecognitionRectangle(
            photo=form.cleaned_data['photo'],
            coordinates=json.dumps(coordinates),
            user_id=request.user.id,
            origin=FaceRecognitionRectangle.USER
        )
        new_rectangle.save()
        points = 25
        Points(
            user=request.user.profile,
            action=Points.ANNOTATION,
            points=points,
            photo=form.cleaned_data['photo'],
            annotation = new_rectangle,
            created=timezone.now()
        ).save()
        response_content = JSONRenderer().render({'id': new_rectangle.id, 'points': points})
        status = 201
    else:
        response_content = 'Invalid data'
        status = 400

    return HttpResponse(response_content, content_type='application/json', status=status)


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

    return new_rectangle.id


def get_rectangles(request, photo_id=None):
    rectangles = []
    if photo_id:
        rectangles = FaceRecognitionRectangleSerializer(
            FaceRecognitionRectangle.objects.filter(photo_id=photo_id, deleted__isnull=True).all(), many=True).data

    return HttpResponse(JSONRenderer().render(rectangles), content_type='application/json')


def add_rectangle_feedback(request, annotation_id):
    face_annotation_feedback_request = FaceAnnotationFeedbackRequest(
        request.user.id,
        annotation_id,
        QueryDict(request.body)
    )
    face_annotation_feedback_service.add_feedback(face_annotation_feedback_request)

    return HttpResponse(JSONRenderer().render({'isOk': True}), content_type='application/json', status=200)


def update_annotation(request: HttpRequest, annotation_id: int):
    if request.method != 'PUT':
        return response.not_supported()

    face_annotation_update_request = FaceAnnotationUpdateRequest(
        QueryDict(request.body),
        annotation_id,
        request.user.id
    )

    is_successful = face_annotation_edit_service.update_face_annotation(face_annotation_update_request)

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


def get_guess_form_html(request: HttpRequest, rectangle_id: int) -> HttpResponse:
    form = FaceRecognitionGuessForm(initial={'rectangle': rectangle_id})
    context = {
        'rectangle_id': rectangle_id,
        'form': form
    }
    return render(request, 'guess_subject.html', context)


def get_subject_image(request: HttpRequest):
    try:
        if(request.rectangle_id):
            rectangle = FaceRecognitionRectangle.objects.filter(pk=request.id).first()
        if (rectangle is None or request.rectangle_id is None):
            rectangle = FaceRecognitionRectangle.objects.first()
        photo = rectangle.subjectPhoto
        with open(settings.MEDIA_ROOT + "/portraits/" + str(rectangle.id), "rb") as f:
            return HttpResponse(f.read(), content_type="image/jpeg")
    except:
        white = Image.new('RGBA', (32, 32), (255,255,255,0))
        response = HttpResponse(content_type="image/jpeg")
        white.save(response, "JPEG")
        return response

def get_subject_data_empty(request):
    return render(request, 'add_subject_data_empty.html')

def get_subject_data(request, subject_id = None):
    profile = request.get_user().profile
    rectangle = None
    nextRectangle = None
    hasUnverified = False
    album_id = request.GET.get('album')
    if album_id is not None and album_id.isdigit():
        album_id = int(album_id, 10)
    else:
        album_id = None
    unverifiedRectangles = FaceRecognitionRectangle.objects.filter(gender=None, deleted=None)
    if album_id is not None:
        albumPhotoIds = AlbumPhoto.objects.filter(album_id=album_id).values_list('photo_id', flat=True)
        unverifiedRectangles = unverifiedRectangles.filter(photo_id__in=albumPhotoIds)
    if unverifiedRectangles.count() > 1:
        rectangles = unverifiedRectangles
    else:
        # TODO: If album_id and subject_id were specified,
        #       but subject_id is not of a photo belonging to album,
        #       then the images will be shown from all guesses of the user.
        #       It should only show from previous guesses of the user, which
        #       are of rectangles belonging to photos which are in album with album_id

        guesses = FaceRecognitionRectangleSubjectDataGuess.objects.filter(guesser_id=profile.id).all().values_list('face_recognition_rectangle_id', flat=True)
        if guesses is None:
            rectangles = FaceRecognitionRectangle.objects.filter(deleted=None)
            if album_id is not None:
                rectangles = rectangles.filter(photo_id__in=albumPhotoIds)
        else:
            rectangles = FaceRecognitionRectangle.objects.filter(deleted=None).exclude(id__in=guesses)
            if album_id is not None:
                rectangles = rectangles.filter(photo_id__in=albumPhotoIds)
            if rectangles.count() == 0:
                rectangles = FaceRecognitionRectangle.objects.filter(deleted=None).annotate(number_of_guesses=Count('face_recognition_guesses')).order_by('-number_of_guesses')
                if album_id is not None:
                    rectangles = rectangles.filter(photo_id__in=albumPhotoIds)
                guessIds = []
                for guess in guesses:
                    if subject_id != str(guess):
                        guessIds.append(guess)
                rectangles = FaceRecognitionRectangle.objects.filter(deleted=None, id=least_frequent(guessIds)).order_by('?')
                if rectangles is not None:
                    nextRectangle = rectangles.first()
                else:
                    allRectangles = FaceRecognitionRectangle.objects.filter(deleted=None)
                    if allRectangles is not None:
                        if album_id is not None:
                            nextRectangle = allRectangles.filter(photo_id__in=albumPhotoIds).order_by('?').first()
                        else:
                            nextRectangle = allRectangles.order_by('?').first()
    if subject_id is None:
        if rectangle is None:
            rectangle = rectangles.order_by('?').first()
    else:
        if rectangle is None:
            rectangle = get_object_or_404(FaceRecognitionRectangle, id=subject_id)
    if rectangle is None:
        if album_id is None:
            rectangle = FaceRecognitionRectangle.objects.order_by('?').first()
        else:
            rectangle = FaceRecognitionRectangle.objects.filter(photo_id__in=albumPhotoIds).order_by('?').first()
    if rectangle is None:
        return render(request, 'add_subject_data_empty.html')
    else:
        if nextRectangle is None:
            nextRectangle = rectangles.exclude(id=rectangle.id).order_by('?').first()
        if nextRectangle is None:
            if album_id is None:
                nextRectangle = FaceRecognitionRectangle.objects.order_by('?').first()
            else:
                nextRectangle = FaceRecognitionRectangle.objects.filter(photo_id__in=albumPhotoIds).order_by('?').first()
        if nextRectangle is None:
            next_action = request.build_absolute_uri(reverse("face_recognition_subject_data", args=(nextRectangle.id,)))
        else:
            next_action = request.build_absolute_uri(reverse("face_recognition_subject_data", args=(nextRectangle.id,)))
            if album_id is not None:
                next_action += "?album=" + str(album_id)

    #These variables are used for debugging purposes, remove when going live
    age = "Undefined"
    gender = "Undefined"
    hasConsensus = False
    if rectangle != None and rectangle.subject_consensus != None:
            hasConsensus = True
            temp = rectangle.subject_consensus.gender
            if rectangle.subject_consensus.gender == 0:
                gender = "Female"
            else:
                gender = "Male"
    else:
        if rectangle.gender == 0:
            gender = "Female"
        if rectangle.gender == 1:
            gender = "Male"
        if rectangle.gender == 2:
            gender = "Not sure"
    if rectangle.age == 0:
        age = "Child"
    if rectangle.age == 1:
        age = "Adult"
    if rectangle.age == 2:
        age = "Elder"
    if rectangle.age == 3:
        age = "Not Sure"

    context = {
        'rectangle': rectangle,
        'photo': rectangle.photo,
        'coordinates': rectangle.coordinates,
        'next_action': next_action,
        'gender': gender,
        'age': age,
        'hasConsensus': hasConsensus
    }
    return render(request, 'add_subject_data.html', context)