import datetime
from uuid import uuid4

from allauth.account.forms import ChangePasswordForm, SetPasswordForm, AddEmailForm
from allauth.account.views import PasswordSetView, PasswordChangeView, EmailView
from allauth.socialaccount.forms import DisconnectForm
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.views import ConnectionsView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _

from ajapaik.ajapaik.forms import RephotoUploadSettingsForm
from ajapaik.ajapaik.models import MyXtdComment, Photo, Dating, GeoTag, PhotoLike, \
    ImageSimilaritySuggestion, Transcription, PhotoViewpointElevationSuggestion, PhotoSceneSuggestion, Profile, \
    ProfileMergeToken
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle
from ajapaik.ajapaik_object_recognition.models import ObjectDetectionAnnotation
from ajapaik.ajapaik_profile.forms import ChangeDisplayNameForm, UserSettingsForm


def user(request, user_id):
    token = ProfileMergeToken.objects.filter(source_profile_id=user_id, used__isnull=False).order_by('used').first()

    if token is not None and token.target_profile is not None:
        return redirect('user', user_id=token.target_profile.id)

    current_profile = request.get_user().profile
    profile = get_object_or_404(Profile, pk=user_id)
    is_current_user = False
    if current_profile == profile:
        is_current_user = True
    if profile.user.is_anonymous:
        commented_pictures_count = 0
    else:
        commented_pictures_count = MyXtdComment.objects.filter(is_removed=False, user_id=profile.id).order_by(
            'object_pk').distinct('object_pk').count()

    curated_pictures_count = Photo.objects.filter(user_id=profile.id, rephoto_of__isnull=True).count()
    datings_count = Dating.objects.filter(profile_id=profile.id).distinct('photo').count()
    face_annotations_count = FaceRecognitionRectangle.objects.filter(user_id=profile.id).count()
    face_annotations_pictures_count = FaceRecognitionRectangle.objects.filter(user_id=profile.id).distinct(
        'photo').count()
    geotags_count = GeoTag.objects.filter(user_id=profile.id).exclude(type=GeoTag.CONFIRMATION).distinct(
        'photo').count()
    geotag_confirmations_count = GeoTag.objects.filter(user_id=profile.id, type=GeoTag.CONFIRMATION).distinct(
        'photo').count()
    object_annotations_count = ObjectDetectionAnnotation.objects.filter(user_id=profile.id).count()
    object_annotations_pictures_count = ObjectDetectionAnnotation.objects.filter(user_id=profile.id).distinct(
        'photo').count()
    photolikes_count = PhotoLike.objects.filter(profile_id=profile.id).distinct('photo').count()
    rephoto_count = Photo.objects.filter(user_id=profile.id, rephoto_of__isnull=False).count()
    rephotographed_pictures_count = Photo.objects.filter(user_id=profile.id, rephoto_of__isnull=False).order_by(
        'rephoto_of_id').distinct('rephoto_of_id').count()
    similar_pictures_count = ImageSimilaritySuggestion.objects.filter(proposer=profile).distinct(
        'image_similarity').count()
    transcriptions_count = Transcription.objects.filter(user=profile).distinct('photo').count()

    photo_viewpoint_elevation_suggestions_ids = PhotoViewpointElevationSuggestion.objects.filter(
        proposer_id=profile.id).distinct('photo').values_list('photo_id', flat=True)
    photo_scene_suggestions_count = PhotoSceneSuggestion.objects.filter(proposer_id=profile.id).distinct(
        'photo').exclude(
        photo_id__in=photo_viewpoint_elevation_suggestions_ids).count()

    action_count = commented_pictures_count + transcriptions_count + \
                   object_annotations_count + face_annotations_count + \
                   curated_pictures_count + geotags_count + \
                   rephoto_count + rephoto_count + datings_count + \
                   similar_pictures_count + geotag_confirmations_count + \
                   photolikes_count + photo_scene_suggestions_count + len(photo_viewpoint_elevation_suggestions_ids)

    user_points = profile.points.aggregate(user_points=Sum('points'))['user_points']
    if user_points is None:
        user_points = 0

    context = {
        'actions': action_count,
        'commented_pictures': commented_pictures_count,
        'curated_pictures': curated_pictures_count,
        'datings': datings_count,
        'face_annotations': face_annotations_count,
        'face_annotations_pictures': face_annotations_pictures_count,
        'favorites_link': '/?order1=time&order2=added&page=1&myLikes=1',
        'geotag_confirmations': geotag_confirmations_count,
        'geotagged_pictures': geotags_count,
        'is_current_user': is_current_user,
        'object_annotations': object_annotations_count,
        'object_annotations_pictures': object_annotations_pictures_count,
        'photo_likes': photolikes_count,
        'photo_suggestions': photo_scene_suggestions_count + len(photo_viewpoint_elevation_suggestions_ids),
        'profile': profile,
        'rephotographed_pictures': rephotographed_pictures_count,
        'rephotos_link': f'/photos/?rephotosBy={str(profile.user_id)}&order1=time&order2=rephotos',
        'rephotos': rephoto_count,
        'similar_pictures': similar_pictures_count,
        'transcriptions': transcriptions_count,
        'user_points': user_points
    }

    return render(request, 'user/user.html', context)


def user_settings_modal(request):
    form = None
    if hasattr(request.user, 'profile'):
        form = UserSettingsForm(data={
            'preferred_language': request.user.profile.preferred_language,
            'newsletter_consent': request.user.profile.newsletter_consent
        })
    context = {
        'form': form,
        'isModal': True
    }

    return render(request, 'user/settings/_user_settings_modal_content.html', context)


def user_settings(request):
    profile = hasattr(request.user, 'profile') and request.user.profile or None

    if not profile:
        return render(request, 'user/settings/user_settings.html', context={})

    invalid = False
    initial = False
    user_settings_form = UserSettingsForm(data={
        'preferred_language': profile.preferred_language,
        'newsletter_consent': profile.newsletter_consent
    })

    context = {'profile': profile}
    token = request.GET.get('token')
    if token:
        token = ProfileMergeToken.objects.filter(token=token, used=None,
                                                 created__gte=datetime.date.today() - datetime.timedelta(
                                                     hours=1)).first()
    else:
        initial = True

    if token is None:
        invalid = not initial
        if profile.is_legit():
            token = ProfileMergeToken(token=str(uuid4()), profile=profile)
            token.save()
        else:
            context['next'] = request.path
    else:
        context['token_profile_social_accounts'] = SocialAccount.objects.filter(user_id=token.profile.user_id)
        context['link'] = reverse('user', args=(token.profile_id,))

    context['next'] = f'{request.path}?token={token.token}'
    display_name_form = ChangeDisplayNameForm(data={'display_name': profile.display_name})
    show_accordion = not invalid and profile.is_legit and not initial
    social_account_form = DisconnectForm(request=request)

    if request.user.has_usable_password():
        password_accordion = {"id": 4, "heading": _("Change password"), "template": "account/password_change_form.html",
                              "form": ChangePasswordForm(), "show_merge_section": None}
    else:
        password_accordion = {"id": 4, "heading": "Set password", "template": "account/password_set_form.html",
                              "form": SetPasswordForm(), "show_merge_section": None}
    context['accordions'] = [
        {"id": 1,
         "heading": _("Change display name"),
         "template": "user/display_name/change_display_name.html",
         "form": display_name_form,
         "show_merge_section": None
         },
        {"id": 2,
         "heading": _("Newsletter and language settings"),
         "template": "user/settings/_user_settings_modal_content.html",
         "form": user_settings_form,
         "show_merge_section": None
         },
        {"id": 3,
         "heading": _("E-mail addresses"),
         "template": "account/email_content.html",
         "form": AddEmailForm(),
         "show_merge_section": None
         },
        password_accordion,
        {"id": 5,
         "heading": _("Account Connections"),
         "template": "socialaccount/connections_content.html",
         "form": social_account_form, "show_merge_section": None
         },
        {"id": 6,
         "heading": _("Merge another Ajapaik account with current one"),
         "template": "user/merge/merge_accounts.html", "form": None
         }
    ]
    return render(request, 'user/settings/user_settings.html',
                  {
                      **context,
                      'invalid': invalid,
                      'initial': initial,
                      'show_accordion': show_accordion,
                      'me': reverse('me'),
                      'profile_social_accounts': SocialAccount.objects.filter(user_id=request.user.id),
                      'token': token
                  })

    return render(request, 'user/display_name/change_display_name.html', context)


def merge_accounts(request):
    context = {}
    token = request.GET.get('token')
    if (hasattr(request.user, 'profile')):
        context['profile'] = request.user.profile
    if token is None:
        if 'profile' in context and request.user.profile.is_legit():
            token = ProfileMergeToken(token=str(uuid4()), profile=request.user.profile)
            token.save()
        context['initial'] = True
    else:
        token = ProfileMergeToken.objects.filter(token=token, used=None,
                                                 created__gte=datetime.date.today() - datetime.timedelta(
                                                     hours=1)).first()
        if token is None:
            context['invalid'] = True
            if 'profile' in context and request.user.profile.is_legit():
                token = ProfileMergeToken(token=str(uuid4()), profile=request.user.profile)
                token.save()
            else:
                context['next'] = request.path
        else:
            context['token_profile_social_accounts'] = SocialAccount.objects.filter(user_id=token.profile.user_id)
            context['link'] = reverse('user', args=(token.profile_id,))
    if token and token.token:
        context['next'] = f'{request.path}?token={token.token}'
    context['me'] = reverse('me')
    context['profile_social_accounts'] = SocialAccount.objects.filter(user_id=request.user.id)
    context['token'] = token

    return render(request, 'user/merge/merge_accounts.html', context)


def me(request):
    return redirect('user', user_id=request.get_user().profile.id)


class MyPasswordSetView(LoginRequiredMixin, PasswordSetView):
    success_url = reverse_lazy('user_settings')


class MyPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    success_url = reverse_lazy('user_settings')


class MyConnectionsView(LoginRequiredMixin, ConnectionsView):
    success_url = reverse_lazy('user_settings')


class MyEmailView(LoginRequiredMixin, EmailView):
    success_url = reverse_lazy('user_settings')


def rephoto_upload_settings_modal(request):
    form = None
    if (hasattr(request.user, 'profile')):
        profile = request.user.profile
        form = RephotoUploadSettingsForm(
            data={'wikimedia_commons_rephoto_upload_consent': profile.wikimedia_commons_rephoto_upload_consent})

    context = {
        'form': form,
        'isModal': True
    }

    return render(request, 'rephoto_upload/_rephoto_upload_settings_modal_content.html', context)
