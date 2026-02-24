import datetime

from django.conf import settings
from django.contrib.auth import login
from django.http import JsonResponse
from django.utils import timezone
from django.utils.translation import gettext as _

from ajapaik.ajapaik.api import AjapaikAPIView, PLEASE_LOGIN
from ajapaik.ajapaik.models import ProfileMergeToken
from ajapaik.ajapaik_profile.utils import merge_profiles

EXPIRED_TOKEN = _('Expired token')
INVALID_TOKEN = _('Invalid token')
MISSING_PARAMETER_TOKEN = _('Required parameter, token is missing')
PROFILE_MERGE_LOGIN_PROMPT = _(
    'Please login with a different account, you are currently logged in with the same account '
    'that you are merging from')
PROFILE_MERGE_SUCCESS = _('Contributions and settings from the other account were added to current')


class MergeProfiles(AjapaikAPIView):
    '''
    API endpoint for merging two users' points, photos, annotations, datings, etc..
    '''

    def post(self, request, format=None):
        reverse = request.POST['reverse']
        token = request.POST['token']
        if token is None:
            return JsonResponse({'error': MISSING_PARAMETER_TOKEN}, status=400)
        profile_merge_token = ProfileMergeToken.objects.filter(token=token).first()
        if profile_merge_token is None:
            return JsonResponse({'error': INVALID_TOKEN}, status=401)
        if profile_merge_token.used is not None or (
                profile_merge_token.created < (timezone.now() - datetime.timedelta(hours=1))):
            return JsonResponse({'error': EXPIRED_TOKEN}, status=401)
        if request.user and request.user.profile and request.user.profile.is_legit():
            if request.user.profile.id != profile_merge_token.profile_id:
                if reverse == 'true':
                    merge_profiles(request.user.profile, profile_merge_token.profile)
                    profile_merge_token.target_profile = request.user.profile
                    profile_merge_token.source_profile = profile_merge_token.profile
                else:
                    merge_profiles(profile_merge_token.profile, request.user.profile)
                    profile_merge_token.target_profile = profile_merge_token.profile
                    profile_merge_token.source_profile = request.user.profile
                    login(request, request.user, backend=settings.AUTHENTICATION_BACKENDS[0])
                profile_merge_token.used = datetime.datetime.now()
                profile_merge_token.save()
                return JsonResponse({'message': PROFILE_MERGE_SUCCESS})
            else:
                return JsonResponse({'message': PROFILE_MERGE_LOGIN_PROMPT})
        else:
            return JsonResponse({'error': PLEASE_LOGIN}, status=401)
