from __future__ import with_statement

from contextlib import closing
from json import loads

from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import View

from project.ajapaik.mixins import FacebookMixin

APP_ID = settings.FACEBOOK_APP_ID

class FacebookHandler(FacebookMixin, View):

    def get(self, *args, **kwargs):
        stage = kwargs['stage']

        if stage == 'login':
            self.request.log_action("facebook.login")
            self.next()
            return redirect(self.login_url(self.fbview_url("auth")))

        elif stage == 'auth':
            self.request.log_action("facebook.auth")

            return redirect(self.auth_url(self.fbview_url("done"), ["public_profile", "email", "user_friends"]))

        elif stage == 'done': 
            next_uri = "/"
            if "fb_next" in self.request.session:
                next_uri = self.request.session["fb_next"]
                del self.request.session["fb_next"]
                self.request.session.modified = True

            code = self.request.GET.get("code")
            if code:
                try:
                    token = loads(self.url_read(self.token_url(code)))
                    data = self.profile_url(token)
                except Exception, e:
                    self.request.log_action("facebook.url_read.exception", {"message": unicode(e)})
                    raise
    
                # create or update profile data
                profile = self.user_profile(data)

                if self.request.user.is_authenticated():
                    self.request.log_action("facebook.merge", {"id": data.get("id")}, profile)
                    profile.merge_from_other(self.request.get_user().profile)
                    self.request.set_user(profile.user)
                
                self.request.log_action("facebook.connect", {"data": data}, profile)
                return redirect(next_uri)

            self.request.log_action("facebook.error", {"params": self.request.GET})
            return redirect("/fb_error")