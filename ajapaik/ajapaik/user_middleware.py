# http://docs.djangoproject.com/en/dev/topics/http/middleware/
# http://docs.djangoproject.com/en/dev/topics/auth/
import secrets
import string
from functools import partial

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils.deprecation import MiddlewareMixin


def get_user(request):
    if request.user and request.user.is_authenticated:
        return request.user
    else:
        if any(s in request.META.get('HTTP_USER_AGENT', []) for s in settings.BOT_USER_AGENTS):
            user = authenticate(request=request, username=settings.BOT_USERNAME)
        else:
            session_id = request.session._get_or_create_session_key()
            user = authenticate(request=request, username=session_id)

        login(request=request, user=user, backend='allauth.account.auth_backends.AuthenticationBackend')

        return user


def set_user(request, user):
    logout(request)
    login(request=request, user=user, backend='allauth.account.auth_backends.AuthenticationBackend')

    return user


class UserMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.get_user = partial(get_user, request)
        request.set_user = partial(set_user, request)


class AuthBackend:
    def authenticate(self, request=None, username=None, password=None, user=None):
        if user is not None:
            return user
        if password is not None:
            try:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    return user
                else:
                    return None
            except ObjectDoesNotExist:
                return None

        if username == settings.BOT_USERNAME:
            bot_username = f'_bot_{username}'
            try:
                user = User.objects.get(username=bot_username)
                return user
            except ObjectDoesNotExist:
                user = User.objects.create_user(username=bot_username)
                user.save()

                return user

        alphabet = string.ascii_letters + string.digits
        random_username = f"_{username[:25]}_{''.join(secrets.choice(alphabet) for i in range(3))}"
        user = User.objects.create_user(username=random_username)
        user.save()

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
