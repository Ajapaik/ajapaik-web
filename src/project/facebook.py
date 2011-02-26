from __future__ import with_statement

from urllib import urlencode
from urllib2 import quote, urlopen
from project.models import Profile
from contextlib import closing

from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.simplejson import loads

APP_ID = '201052296573134'
APP_KEY = '32d6e5e8fae03b1bdf1c1af0e685df35'
APP_SECRET = 'c5958185bb5e148c9f4346d3b6d924e1'

def url_read(uri):
    with closing(urlopen(uri)) as request:
        return request.read()

def login_url(redirect_uri):
    return "https://www.facebook.com/dialog/oauth?client_id=%s&redirect_uri=%s" % (APP_ID, quote(redirect_uri))

def auth_url(redirect_uri, scope=[]):
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
    return request.build_absolute_uri('/facebook/%s' % stage)

def facebook_handler(request, stage):
    if stage == 'login':
    	request.log_action("facebook.login")
        return redirect(login_url(fbview_url(request, 'auth')))
    elif stage == 'auth':
    	request.log_action("facebook.auth")
        return redirect(auth_url(fbview_url(request, 'done')))
    elif stage == 'done':
        code = request.GET.get("code")
        if code:
            # TODO: check for existing profile
            token = url_read(token_url(request, code))
            
            profile = request.get_user().get_profile()
            profile.fb_token = token
            
            data = loads(url_read(profile_url(token)))
            profile.user.first_name = data.get("first_name")
            profile.user.last_name = data.get("last_name")
            profile.fb_id = data.get("id")
            profile.fb_name = data.get("id")
            profile.fb_link = data.get("link")
            profile.save()

            request.log_action("facebook.connect", {'data': data}, profile)
            
            return HttpResponse(repr(data))
        else:
    	    request.log_action("facebook.error")
            return redirect('/fb_error')
        
        return redirect('/')
        
