import requests
from allauth.socialaccount import providers
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import WikimediaCommonsProvider
from .client import WikimediaCommonsOAuth2Client

class WikimediaCommonsOAuth2Adapter(OAuth2Adapter):
    provider_id = WikimediaCommonsProvider.id
    wiki_oauth_url = 'https://commons.wikimedia.org/w/rest.php/oauth2'
    access_token_url = wiki_oauth_url + '/access_token'
    access_token_method = 'POST'
    authorize_url = wiki_oauth_url + '/authorize' 
    authorize_url_method = 'GET'
    profile_url = wiki_oauth_url + '/resource/profile'

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'Bearer {0}'.format(token.token)}
        resp = requests.get(self.profile_url, headers=headers)
        resp.raise_for_status()
        extra_data = resp.json()
        login = self.get_provider() \
            .sociallogin_from_response(request,
                                       extra_data) 
        return login

class WikimediaCommonsOAuth2CallbackView(OAuth2CallbackView):
    """ Custom OAuth2CallbackView to return WikimediaCommonsOAuth2Client """

    def get_client(self, request, app):
        client = super(WikimediaCommonsOAuth2CallbackView, self).get_client(request, app)
        wikimedia_commons_client = WikimediaCommonsOAuth2Client(
            client.request, client.consumer_key, client.consumer_secret,
            client.access_token_method, client.access_token_url,
            client.callback_url, client.scope)
        return wikimedia_commons_client


oauth2_login = OAuth2LoginView.adapter_view(WikimediaCommonsOAuth2Adapter)
oauth2_callback = WikimediaCommonsOAuth2CallbackView.adapter_view(WikimediaCommonsOAuth2Adapter)
