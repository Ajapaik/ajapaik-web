# http://docs.djangoproject.com/en/dev/topics/http/middleware/
# http://docs.djangoproject.com/en/dev/topics/auth/
from functools import partial

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from project.ajapaik.models import Action
from project.ajapaik.settings import BOT_USER_AGENTS, BOT_USERNAME


def get_user(request):
    if request.user and request.user.is_authenticated():
        return request.user
    else:
        if request.META \
                and 'HTTP_USER_AGENT' in request.META \
                and any(s in request.META['HTTP_USER_AGENT'] for s in BOT_USER_AGENTS):
            user = authenticate(username=BOT_USERNAME)
        else:
            session_id = request.session._get_or_create_session_key()
            user = authenticate(username=session_id)
        login(request, user)

        return user


def set_user(request, user):
    logout(request)
    authenticate(user=user)
    login(request, user)

    return user


class UserMiddleware(object):
    def process_request(self, request):
        request.get_user = partial(get_user, request)
        request.set_user = partial(set_user, request)
        request.log_action = partial(Action.log, request=request)


class AuthBackend(object):
    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = True

    def authenticate(self, username=None, password=None, user=None):
        if user is not None:
            return user
        if password is not None:
            try:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    Action.log('user_middleware.login.success', {'username': username})

                    return user
                else:
                    Action.log('user_middleware.login.error', {'username': username})

                    return None
            except ObjectDoesNotExist:
                return None

        if username == BOT_USERNAME:
            bot_username = u'_bot_%s' % (username)
            try:
                user = User.objects.get(username=bot_username)
                Action.log('user_middleware.login.success', {'username': bot_username})

                return user
            except ObjectDoesNotExist:
                user = User.objects.create_user(username=bot_username)
                user.save()
                Action.log('user_middleware.create.bot', related_object=user)

                return user

        random_username = u'_%s_%s' % (username[:25], User.objects.make_random_password(length=3))
        user = User.objects.create_user(username=random_username)
        user.save()
        Action.log('user_middleware.create', related_object=user)

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
