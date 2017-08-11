from contextlib import closing
from json import loads
from urllib import urlencode
from urllib2 import quote, urlopen

from django.conf import settings

from project.ajapaik.models import Profile

APP_ID = settings.FACEBOOK_APP_ID
APP_KEY = settings.FACEBOOK_APP_KEY
APP_SECRET = settings.FACEBOOK_APP_SECRET


class FacebookMixin(object):

    def __init__(self, *args, **kwargs):
        return super(FacebookMixin, self).__init__(*args, **kwargs)

    def url_read(self, uri):
        with closing(urlopen(uri)) as request:
            return request.read()

    def login_url(self, redirect_uri):
        return "https://www.facebook.com/dialog/oauth?client_id=%s&redirect_uri=%s" % (APP_ID, quote(redirect_uri))

    def auth_url(self, redirect_uri, scope=None):
        if not scope:
            scope = []

        return "https://www.facebook.com/dialog/oauth?client_id=%s&redirect_uri=%s&scope=%s" % (
        APP_ID, quote(redirect_uri), quote(",".join(scope)))

    def token_url(self, code):
        return "https://graph.facebook.com/oauth/access_token?" + \
               urlencode({"client_id": APP_ID,
                          "redirect_uri": self.fbview_url("done"),
                          "client_secret": APP_SECRET,
                          "code": code})

    def profile_url(self, token):
        profile = loads(self.url_read("https://graph.facebook.com/v2.3/me?access_token=" + token['access_token']))
        name = profile.get('name')
        first_name, last_name = name.split(' ')

        return {
            "first_name" : first_name,
            "last_name"  : last_name,
            "fb_id"      : profile.get('id'),
            "fb_name"    : name,
            "fb_email"   : profile.get('fb_email'),
            "fb_token"   : token.get('access_token')
        }

    def fbview_url(self, stage):
        return self.request.build_absolute_uri("/facebook/%s/" % stage)

    def next(self):
        if 'next' in self.request.GET:
            self.request.session["fb_next"] = self.request.GET['next']
            self.request.session.modified = True
        elif "HTTP_REFERER" in self.request.META:
            self.request.session["fb_next"] = self.request.META["HTTP_REFERER"]
            self.request.session.modified = True
    
    def user_profile(self, data):
        try:
            profile = Profile.objects.get(fb_id=data.get('fb_id'))
            user = profile.user
        except Profile.DoesNotExist:
            user = self.request.get_user()
            profile = user.profile

        for k, v in data.items():
            setattr(profile, k, v)
            setattr(user, k, v)
        user.save()
        profile.save()

        return profile

