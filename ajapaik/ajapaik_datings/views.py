import datetime
import json

from django.conf import settings
from django.http import HttpResponse

from ajapaik.ajapaik.forms import DatingSubmitForm, DatingConfirmForm
from ajapaik.ajapaik.models import Dating, Points, DatingConfirmation, Photo
from ajapaik.ajapaik.serializers import DatingSerializer


def submit_dating(request):
    profile = request.get_user().profile
    form = DatingSubmitForm(request.POST.copy())
    confirm_form = DatingConfirmForm(request.POST)
    form.data['profile'] = profile.id
    if form.is_valid():
        dating = form.save(commit=False)
        if not dating.start:
            dating.start = datetime.datetime.strptime('01011000', '%d%m%Y').date()
        if not dating.end:
            dating.end = datetime.datetime.strptime('01013000', '%d%m%Y').date()
        p = form.cleaned_data['photo']
        dating_exists = Dating.objects.filter(profile=profile, raw=dating.raw, photo=p).exists()
        if not dating_exists:
            dating.save()
            p.latest_dating = dating.created
            if not p.first_dating:
                p.first_dating = dating.created
            confirmation_count = 0
            for each in p.datings.all():
                confirmation_count += each.confirmations.count()
            p.dating_count = p.datings.count() + confirmation_count
            p.light_save()
            Points(
                user=profile,
                action=Points.DATING,
                photo=form.cleaned_data['photo'],
                dating=dating,
                points=settings.DATING_POINTS,
                created=dating.created
            ).save()
            return HttpResponse('OK')
        return HttpResponse('Dating exists', status=400)
    elif confirm_form.is_valid():
        original_dating = confirm_form.cleaned_data['id']
        confirmation_exists = DatingConfirmation.objects.filter(confirmation_of=original_dating,
                                                                profile=profile).exists()
        if not confirmation_exists and original_dating.profile != profile:
            new_confirmation = DatingConfirmation(
                confirmation_of=original_dating,
                profile=profile
            )
            new_confirmation.save()
            p = original_dating.photo
            p.latest_dating = new_confirmation.created
            confirmation_count = 0
            for each in p.datings.all():
                confirmation_count += each.confirmations.count()
            p.dating_count = p.datings.count() + confirmation_count
            p.light_save()
            Points(
                user=profile,
                action=Points.DATING_CONFIRMATION,
                dating_confirmation=new_confirmation,
                points=settings.DATING_CONFIRMATION_POINTS,
                photo=p,
                created=new_confirmation.created
            ).save()
            return HttpResponse('OK')
        else:
            return HttpResponse('Already confirmed or confirming your own dating', status=400)
    else:
        return HttpResponse('Invalid data', status=400)


def get_datings(request, photo_id):
    photo = Photo.objects.filter(pk=photo_id).first()
    profile = request.get_user().profile
    context = {}
    if photo:
        datings = photo.datings.order_by('created').prefetch_related('confirmations')
        for each in datings:
            each.this_user_has_confirmed = each.confirmations.filter(profile=profile).exists()
        datings_serialized = DatingSerializer(datings, many=True).data
        context['datings'] = datings_serialized

    return HttpResponse(json.dumps(context), content_type='application/json')
