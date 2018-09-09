from allauth.socialaccount.providers.oauth.client import (OAuthClient,
                                                          get_token_prefix)
from allauth.socialaccount.providers.oauth.views import (OAuthAdapter,
                                                         OAuthCallbackView,
                                                         OAuthLoginView)
from mwoauth import ConsumerToken, Handshaker

from .provider import MediaWikiProvider


class MediaWikiClient(OAuthClient):
    def _get_request_token(self):
        """
        Obtain a temporary request token to authorize an access token and to
        sign the request to obtain the access token
        """
        if self.request_token is None:
            handshaker = Handshaker(
                'https://en.wikipedia.org/w/index.php',
                ConsumerToken(self.consumer_key, self.consumer_secret)
            )
            redirect, request_token = handshaker.initiate()
            self.request_token = {
                'oauth_token': request_token.key,
                'oauth_token_secret': request_token.secret
            }
            self.request.session['oauth_%s_request_token' % get_token_prefix(
                self.request_token_url)] = self.request_token
        return self.request_token


class MediaWikiLoginView(OAuthLoginView):
    def _get_client(self, request, callback_url):
        provider = self.adapter.get_provider()
        app = provider.get_app(request)
        scope = ' '.join(provider.get_scope(request))
        parameters = {}
        if scope:
            parameters['scope'] = scope
        client = MediaWikiClient(request, app.client_id, app.secret,
                                 self.adapter.request_token_url,
                                 self.adapter.access_token_url,
                                 callback_url,
                                 parameters=parameters, provider=provider)
        return client


class MediaWikiAuthAdapter(OAuthAdapter):
    provider_id = MediaWikiProvider.id
    request_token_url = 'https://en.wikipedia.org/w/index.php'
    access_token_url = 'https://en.wikipedia.org/w/index.php'
    authorize_url = 'https://en.wikipedia.org/w/index.php'

    def complete_login(self, request, app, token, response):
        return


oauth_login = MediaWikiLoginView.adapter_view(MediaWikiAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(MediaWikiAuthAdapter)
