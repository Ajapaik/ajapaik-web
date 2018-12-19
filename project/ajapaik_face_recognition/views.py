import datetime
import json
from collections import Counter, OrderedDict

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
# FIXME: It's crazy we're importing this from an experimental sub-project
from rest_framework.renderers import JSONRenderer

from project.ajapaik.then_and_now_tours import user_has_confirmed_email
from project.ajapaik_face_recognition.forms import FaceRecognitionAddSubjectForm, FaceRecognitionGuessForm, \
    FaceRecognitionRectangleSubmitForm, FaceRecognitionRectangleFeedbackForm
from project.ajapaik_face_recognition.models import FaceRecognitionUserGuess, FaceRecognitionRectangle, \
    FaceRecognitionRectangleFeedback
from project.ajapaik_face_recognition.serializers import FaceRecognitionRectangleSerializer


@user_passes_test(user_has_confirmed_email, login_url='/accounts/login/')
def add_subject(request):
    form = FaceRecognitionAddSubjectForm()
    context = {'form': form}
    status = 200
    if request.method == 'POST':
        form = FaceRecognitionAddSubjectForm(request.POST.copy())
        context['form'] = form
        if form.is_valid():
            new_subject = form.save(commit=False)
            new_subject.user_id = request.user.id
            new_subject.save()

            status = 201
            context['message'] = 'OK'
        else:
            status = 400
            context['message'] = 'Invalid data'

    return render_to_response('add_subject.html', RequestContext(request, context), status=status)


class OrderedCounter(Counter, OrderedDict):
    pass


@user_passes_test(user_has_confirmed_email, login_url='/accounts/login/')
def guess_subject(request):
    status = 200
    if request.method == 'POST':
        form = FaceRecognitionGuessForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            rectangle = form.cleaned_data['rectangle']
            new_guess = FaceRecognitionUserGuess(
                subject=subject,
                rectangle=rectangle,
                user_id=request.user.id
            )
            new_guess.save()
            # TODO: Verify this works correctly once we have more data
            guesses_so_far_for_this_rectangle = FaceRecognitionUserGuess.objects.filter(rectangle=rectangle)\
                .distinct('user').order_by('user', '-created').all()
            subject_counts = OrderedCounter(g.subject.id for g in guesses_so_far_for_this_rectangle)
            rectangle.subject_consensus_id = subject_counts.keys()[0]
            rectangle.save()
            # TODO: Is this needed?
            subject.photos.add(rectangle.photo)
            status = 201

            return HttpResponse(JSONRenderer().render({'id': new_guess.id}), content_type='application/json',
                                status=status)

    return HttpResponse('OK', status=status)


def get_subjects(request):
    # TODO: Get list of known subjects to refresh photoview or modal asych?
    pass


@user_passes_test(user_has_confirmed_email, login_url='/accounts/login/')
def add_rectangle(request):
    form = FaceRecognitionRectangleSubmitForm(request.POST.copy())
    if form.is_valid():
        photo = form.cleaned_data['photo']
        width_scale = float(form.cleaned_data['seen_width']) / float(photo.width)
        height_scale = float(form.cleaned_data['seen_height']) / float(photo.height)
        # jQuery plugin gives x1, y1 topLeft, x2, y2 bottomRight
        # DB stores (top, right, bottom, left)
        coordinates = [
            int(float(form.cleaned_data['y1']) / height_scale),
            int(float(form.cleaned_data['x2']) / width_scale),
            int(float(form.cleaned_data['y2']) / height_scale),
            int(float(form.cleaned_data['x1']) / width_scale)
        ]
        new_rectangle = FaceRecognitionRectangle(
            photo=form.cleaned_data['photo'],
            coordinates=json.dumps(coordinates),
            user_id=request.user.id
        )
        new_rectangle.save()

        # TODO: DRY
        return HttpResponse(JSONRenderer().render({'id': new_rectangle.id}), content_type='application/json')
    else:
        return HttpResponse('Invalid data', status=400)


def get_rectangles(request, photo_id=None):
    rectangles = []
    if photo_id:
        rectangles = FaceRecognitionRectangleSerializer(
            FaceRecognitionRectangle.objects.filter(photo_id=photo_id, deleted__isnull=True).all(), many=True).data

    return HttpResponse(JSONRenderer().render(rectangles), content_type='application/json')


# Essentially means 'complain to get it deleted'
@user_passes_test(user_has_confirmed_email, login_url='/accounts/login/')
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
        if not new_feedback.is_correct and rectangle.user_id == request.user.id:
            rectangle.deleted = datetime.datetime.now()
            rectangle.save()
            deleted = True
            # TODO: Also update Photo.people or implement asking of people some other way

        # TODO: DRY
        return HttpResponse(JSONRenderer().render({'deleted': deleted}), content_type='application/json')
    else:
        return HttpResponse(JSONRenderer().render({'deleted': deleted}), content_type='application/json', status=400)


def get_guess_form_html(request, rectangle_id):
    form = FaceRecognitionGuessForm(initial={
        'rectangle': rectangle_id
    })

    return render_to_response('guess_subject.html', RequestContext(request, {
        'rectangle_id': rectangle_id,
        'form': form
    }))
