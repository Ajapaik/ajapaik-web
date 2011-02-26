# http://docs.djangoproject.com/en/dev/topics/http/middleware/
# http://docs.djangoproject.com/en/dev/topics/auth/

from project import models
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from functools import partial
import sys

def get_user(request):
    if request.user.is_authenticated():
        return request.user
    else:
        user = authenticate(username=request.session.session_key)
        login(request, user)
        return user

class UserMiddleware(object):
    def process_request(self, request):
        request.get_user = partial(get_user, request=request)
        request.log_action = partial(models.Action.log, request=request)

class AuthBackend(object):
    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = True

    def authenticate(self, username, password=None):
        if password is not None:
            user = User.objects.get(username=username)
            if user.check_password(password):
                models.Action.log("user_middleware.login.success", {'username': username})
                return user
            else:
                models.Action.log("user_middleware.login.error", {'username': username})
                return None

        user = User(username="_"+username[:28])
        user.save()
        models.Action.log("user_middleware.create", related_object=user)
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
