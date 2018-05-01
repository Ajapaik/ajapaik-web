from django.utils.cache import patch_vary_headers
from django.utils import translation
from django.shortcuts import redirect
from project.ajapaik import settings


class ForceDefaultLanguageMiddleware(object):
    """
    Ignore Accept-Language HTTP headers

    This will force the I18N machinery to always choose settings.LANGUAGE_CODE
    as the default initial language, unless another one is set via sessions or
    cookies

    Should be installed *before* any middleware that checks
    request.META['HTTP_ACCEPT_LANGUAGE'], namely
    django.middleware.locale.LocaleMiddleware
    """
    def process_request(self, request):
        if request.META.has_key('HTTP_ACCEPT_LANGUAGE'):
            del request.META['HTTP_ACCEPT_LANGUAGE']


class SessionBasedLocaleWithRedirectMiddleware(object):
    """
    This Middleware saves the desired content language in the user session.
    The SessionMiddleware has to be activated.
    """
    def process_request(self, request):
        if 'language' in request.POST:
            language = request.POST['language']
            request.session['language'] = language
        elif 'language' in request.GET:
            language = request.GET['language']
            request.session['language'] = language
        elif 'language' in request.session:
            language = request.session['language']
        else:
            language = settings.LANGUAGE_CODE

        for lang in settings.LANGUAGES:
            if lang[0] == language and language != translation.get_language():
                translation.activate(language)

        request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        patch_vary_headers(response, ('Accept-Language',))
        if 'Content-Language' not in response:
            response['Content-Language'] = translation.get_language()
        translation.deactivate()

        if 'redirect_to' in request.POST or 'redirect_to' in request.GET:
            if 'redirect_to' in request.POST:
                return redirect(request.GET['redirect_to'])
            elif 'redirect_to' in request.GET:
                return redirect(request.GET['redirect_to'])

        return response


class IsUserDummyMiddleware(object):
    """
    Determinates if current logined user is dummy. Before allauth integration
    we had created and login users on any server touch.
    """

    def _is_user_dummy(self, user):
        if user.is_anonymous():
            return False
        if user.email in (None, '') \
                and user.profile.google_plus_id is None \
                and user.profile.fb_id is None \
                and user.profile.google_plus_email in (None, '') \
                and user.profile.fb_email in (None, ''):
            return True
        else:
            return False

    def process_request(self, request):
        user = request.user
        user.is_dummy = self._is_user_dummy(user)
        if user.is_dummy:
            # Allauth logout user during signup so we need to preserve dummy
            # user to be able do user data transfer.
            request.dummy_user = request.user


class IsUserContributed(object):
    """
    Determinates is current user have contributed to Ajapaik. e.g. uploaded
    rephotos, geotagged photos/images, submit datings etc.
    """

    def process_request(self, request):
        user = request.user
        if user.is_anonymous():
            user.is_contributed = False
            return
        if user.profile.points.all() or user.profile.score:
            user.is_contributed = True
        else:
            user.is_contributed = False
