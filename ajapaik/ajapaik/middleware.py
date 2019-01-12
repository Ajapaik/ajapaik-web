from django.utils.cache import patch_vary_headers
from django.utils import translation
from django.shortcuts import redirect
from ajapaik import settings


class ForceDefaultLanguageMiddleware(object):
    """
    Ignore Accept-Language HTTP headers

    This will force the I18N machinery to always choose settings.LANGUAGE_CODE
    as the default initial language, unless another one is set via sessions or cookies

    Should be installed *before* any middleware that checks request.META['HTTP_ACCEPT_LANGUAGE'],
    namely django.middleware.locale.LocaleMiddleware
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