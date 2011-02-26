from urllib import urlencode
from urllib2 import quote, urlopen
from project.models import Profile

from django.shortcuts import redirect

APP_ID = '201052296573134'
APP_KEY = '32d6e5e8fae03b1bdf1c1af0e685df35'
APP_SECRET = 'c5958185bb5e148c9f4346d3b6d924e1'

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

def fbview_url(request, stage):
    return request.build_absolute_uri('/facebook/%s' % stage)

def facebook_handler(request, stage):
    if stage == 'login':
        return redirect(login_url(fbview_url(request, 'auth')))
    elif stage == 'auth':
        return redirect(auth_url(fbview_url(request, 'done')))
    elif stage == 'done':
        code = request.GET.get("code")
        if code:
            token = urlopen(token_url(request, code)).read()
            profile = request.get_user().get_profile()
            profile.fb_token = token
            profile.save()
        else:
            return redirect('/fb_error')
        
        return redirect('/')
        
