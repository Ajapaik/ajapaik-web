from ujson import loads

import httplib2
import os
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from oauth2client import xsrfutil
from oauth2client.client import flow_from_clientsecrets
from oauth2client.django_orm import Storage

from project.ajapaik.models import CredentialsModel, Profile

CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

FLOW = flow_from_clientsecrets(
    CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email',
    redirect_uri=settings.GOOGLE_PLUS_OAUTH2_CALLBACK_URL)


def google_login(request):
    storage = Storage(CredentialsModel, 'id', request.user.id, 'credential')
    credential = storage.get()
    next_uri = '/'
    if 'next' in request.GET:
        request.session['google_plus_next'] = request.GET['next']
        next_uri = request.GET['next']
        request.session.modified = True
    if credential is None or credential.invalid == True:
        FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY, request.user)
        authorize_url = FLOW.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)
    return HttpResponseRedirect(next_uri)


def auth_return(request):
    if 'state' not in request.REQUEST or not xsrfutil.validate_token(settings.SECRET_KEY, str(request.REQUEST['state']),
                                                                     request.user):
        return HttpResponseBadRequest()
    credential = FLOW.step2_exchange(request.REQUEST)
    http = httplib2.Http()
    http = credential.authorize(http)
    (resp_headers, content) = http.request('https://www.googleapis.com/oauth2/v1/userinfo', 'GET')
    content = loads(content)
    try:
        profile = Profile.objects.get(google_plus_id=content['id'])
        request_profile = request.get_user().profile
        if request.user.is_authenticated():
            request.log_action('google_plus.merge', {'id': content['id']}, profile)
            profile.merge_from_other(request_profile)
        user = profile.user
        request.set_user(user)
    except Profile.DoesNotExist:
        user = request.get_user()
        profile = user.profile
    storage = Storage(CredentialsModel, 'id', request.user, 'credential')
    storage.put(credential)
    profile.update_from_google_plus_data(credential, content)
    request.log_action('google_plus.connect', {'data': content}, profile)
    next_uri = '/'
    if 'google_plus_next' in request.session:
        next_uri = request.session['google_plus_next']
        del request.session['google_plus_next']
        request.session.modified = True
    return HttpResponseRedirect(next_uri)
