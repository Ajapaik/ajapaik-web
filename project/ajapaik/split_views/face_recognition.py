import datetime
import json

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from project.ajapaik.models import FaceRecognitionRectangle, FaceRecognitionRectangleFeedback, FaceRecognitionUserGuess
from project.ajapaik.split_forms.face_recognition import FaceRecognitionRectangleSubmitForm, \
    FaceRecognitionRectangleFeedbackForm, FaceRecognitionAddSubjectForm, FaceRecognitionGuessForm
from project.ajapaik.then_and_now_tours import user_has_confirmed_email


# Probably a good idea to not allow anonymous contributions. So easy to mess with our data that way,
@user_passes_test(user_has_confirmed_email, login_url='/accounts/login/')
def add_subject(request):
    context = {}
    if request.method == 'POST':
        form = FaceRecognitionAddSubjectForm(request.POST.copy())
        if form.is_valid():
            new_subject = form.save(commit=False)
            new_subject.user_id = request.user.id
            new_subject.save()

            return HttpResponse('OK')
        else:
            return HttpResponse('Invalid data', status=400)
    else:
        form = FaceRecognitionAddSubjectForm()
        context['form'] = form

        # TODO: Form needs datepicker?
        return render_to_response('face_recognition/add_subject.html', RequestContext(request, context))


@user_passes_test(user_has_confirmed_email, login_url='/accounts/login/')
def guess_subject(request):
    form = FaceRecognitionGuessForm(request.POST.copy())
    if form.is_valid():
        # TODO: Clean up
        FaceRecognitionUserGuess(
            subject=form.cleaned_data['subject'],
            rectangle=form.cleaned_data['rectangle'],
            user_id=request.user.id
        ).save()
        form.cleaned_data['subject'].photos.add(form.cleaned_data['rectangle'].photo)
        form.cleaned_data['subject'].save()

    return HttpResponse('OK')


@user_passes_test(user_has_confirmed_email, login_url='/accounts/login/')
def add_rectangle(request):
    form = FaceRecognitionRectangleSubmitForm(request.POST.copy())
    if form.is_valid():
        photo = form.cleaned_data['photo']
        width_scale = form.cleaned_data['seen_width'] / photo.width
        height_scale = form.cleaned_data['seen_height'] / photo.height
        # jQuery plugin gives x1, y1 topLeft, x2, y2 bottomRight
        # DB stores (top, right, bottom, left)
        coordinates = [
            int(form.cleaned_data['y1'] * height_scale),
            int(form.cleaned_data['x2'] * width_scale),
            int(form.cleaned_data['y2'] * height_scale),
            int(form.cleaned_data['x1'] * width_scale)
        ]
        FaceRecognitionRectangle(
            photo=form.cleaned_data['photo'],
            coordinates=json.dumps(coordinates),
            user_id=request.user.id
        ).save()

        return HttpResponse('OK')
    else:
        return HttpResponse('Invalid data', status=400)


# Essentially means 'complain to get it deleted'
@user_passes_test(user_has_confirmed_email, login_url='/accounts/login/')
def add_rectangle_feedback(request):
    form = FaceRecognitionRectangleFeedbackForm(request.POST.copy())
    if form.is_valid():
        rectangle = form.cleaned_data['rectangle']
        new_feedback = FaceRecognitionRectangleFeedback(
            rectangle=rectangle,
            user_id=request.user.id,
            is_correct=form.cleaned_data['is_correct']
        )
        new_feedback.save()
        # TODO: Allow the owner to delete their rectangle at will, others should go through some manual vetting process?
        if not new_feedback.is_correct:
            rectangle.deleted = datetime.datetime.now()
            rectangle.save()

        return HttpResponse('OK')
    else:
        return HttpResponse('Invalid data', status=400)
