from __future__ import with_statement

from urllib import urlencode
from urllib2 import quote, urlopen
from project.home.models import Profile
from contextlib import closing
from django.conf import settings

from django.shortcuts import redirect
from json import loads

APP_ID = '201052296573134'
APP_KEY = settings.FACEBOOK_APP_KEY
APP_SECRET = settings.FACEBOOK_APP_SECRET

def url_read(uri):
    with closing(urlopen(uri)) as request:
        return request.read()

def login_url(redirect_uri):
    return "https://www.facebook.com/dialog/oauth?client_id=%s&redirect_uri=%s" % (APP_ID, quote(redirect_uri))

def auth_url(redirect_uri, scope=None):
    if not scope:
        scope = []
    return "https://www.facebook.com/dialog/oauth?client_id=%s&redirect_uri=%s&scope=%s" % (APP_ID, quote(redirect_uri), quote(",".join(scope)))

def token_url(request, code):
    return "https://graph.facebook.com/oauth/access_token?" + \
            urlencode({'client_id': APP_ID, 
                       'redirect_uri': fbview_url(request, 'done'), 
                       'client_secret': APP_SECRET,
                       'code': code})

def profile_url(token):
    return 'https://graph.facebook.com/me?' + token

def fbview_url(request, stage):
    return request.build_absolute_uri('/facebook/%s/' % stage)

def facebook_handler(request, stage):
    if stage == 'login':
        request.log_action("facebook.login")

        request.session['fb_next'] = request.META['HTTP_REFERER']
        request.session.modified = True
            
        return redirect(login_url(fbview_url(request, 'auth')))
    elif stage == 'auth':
        request.log_action("facebook.auth")
        return redirect(auth_url(fbview_url(request, 'done'), ["user_location", "user_hometown", "user_birthday", "email", "user_friends"]))
    elif stage == 'done':
        
        next_uri = '/'
        
        if 'fb_next' in request.session:
            next_uri = request.session['fb_next']
            del request.session['fb_next']
            request.session.modified = True
        
        code = request.GET.get("code")
        if code:
            # TODO: check for existing profile
            try:
                token = url_read(token_url(request, code))
                data = loads(url_read(profile_url(token)))
            except Exception, e:
                request.log_action("facebook.url_read.exception", {'message': unicode(e)})
                raise

            try:
                profile = Profile.objects.get(fb_id=data.get("id"))
                if request.user.is_authenticated():
                    request.log_action("facebook.merge", {'id': data.get("id")}, profile)
                    profile.merge_from_other(request.user.profile)
                user = profile.user
                request.set_user(user)
            except Profile.DoesNotExist:
                user = request.get_user()
                profile = user.profile
            
            profile.update_from_fb_data(token, data)

            request.log_action("facebook.connect", {'data': data}, profile)
            
            #return HttpResponse(repr(data))
            return redirect(next_uri)
        else:
            request.log_action("facebook.error", {'params': request.GET})
            return redirect('/fb_error')