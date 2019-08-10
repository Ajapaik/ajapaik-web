import datetime
import json
import logging
from collections import Counter, OrderedDict
from typing import Optional, Iterable

from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from django.template import RequestContext
from rest_framework.renderers import JSONRenderer

from ajapaik.ajapaik.models import Photo, Album, AlbumPhoto
from ajapaik.ajapaik_face_recognition.forms import FaceRecognitionGuessForm, \
    FaceRecognitionRectangleSubmitForm, FaceRecognitionRectangleFeedbackForm, FaceRecognitionAddPersonForm
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionUserGuess, FaceRecognitionRectangle, \
    FaceRecognitionRectangleFeedback
from ajapaik.ajapaik_face_recognition.serializers import FaceRecognitionRectangleSerializer

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


def guess_subject(request: HttpRequest) -> HttpResponse:
    status = 200
    if request.method == 'POST':
        form = FaceRecognitionGuessForm(request.POST)
        if form.is_valid():
            subject_album: Album = form.cleaned_data['subject_album']
            rectangle: FaceRecognitionRectangle = form.cleaned_data['rectangle']
            new_guess = FaceRecognitionUserGuess(
                subject_album=subject_album,
                rectangle=rectangle,
                user_id=request.user.id,
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
                               profile=request.user.profile).save()
                    subject_album.save()
                    status = 201
            rectangle.subject_consensus_id = consensus_subject
            rectangle.save()

            return HttpResponse(JSONRenderer().render({'id': new_guess.id}), content_type='application/json',
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
        response_content = JSONRenderer().render({'id': new_rectangle.id})
        status = 201
    else:
        response_content = 'Invalid data'
        status = 400

    return HttpResponse(response_content, content_type='application/json', status=status)


def get_rectangles(request, photo_id=None):
    rectangles = []
    if photo_id:
        rectangles = FaceRecognitionRectangleSerializer(
            FaceRecognitionRectangle.objects.filter(photo_id=photo_id, deleted__isnull=True).all(), many=True).data

    return HttpResponse(JSONRenderer().render(rectangles), content_type='application/json')


# Essentially means 'complain to get it deleted'
def add_rectangle_feedback(request):
    form = FaceRecognitionRectangleFeedbackForm(request.POST.copy())
    deleted = False
    if form.is_valid():
        rectangle = form.cleaned_data['rectangle']
        new_feedback = FaceRecognitionRectangleFeedback(
            rectangle=rectangle,
            user_id=request.user.id,
            is_correct=form.cleaned_data['is_correct']
        )
        new_feedback.save()
        # Allow the owner to delete their own rectangle at will
        # TODO: Some kind of review process to delete rectangles not liked by N people?
        # and rectangle.user_id == request.user.id
        if not new_feedback.is_correct:
            rectangle.deleted = datetime.datetime.now()
            rectangle.save()
            deleted = True
            # TODO: Also update Photo.people or implement asking of people some other way
        status = 200
    else:
        status = 400

    return HttpResponse(JSONRenderer().render({'deleted': deleted}), content_type='application/json', status=status)


def get_guess_form_html(request: HttpRequest, rectangle_id: int) -> HttpResponse:
    form = FaceRecognitionGuessForm(initial={'rectangle': rectangle_id})
    context = {
        'rectangle_id': rectangle_id,
        'form': form
    }
    return render(request, 'guess_subject.html', context)
