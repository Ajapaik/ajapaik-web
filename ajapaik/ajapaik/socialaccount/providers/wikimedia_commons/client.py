from collections import OrderedDict

import requests
from allauth.socialaccount.providers.oauth2.client import (
    OAuth2Client,
    OAuth2Error,
)
from django.utils.http import urlencode


class WikimediaCommonsOAuth2Client(OAuth2Client):

    def get_redirect_url(self, authorization_url, extra_params):
        params = {
            'client_id': self.consumer_key,
            'redirect_uri': self.callback_url,
            'scope': self.scope,
            'response_type': 'code'
        }

        if self.state:
            params['state'] = self.state

        params.update(extra_params)
        sorted_params = OrderedDict()

        for param in sorted(params):
            sorted_params[param] = params[param]

        return f'{authorization_url}?{urlencode(sorted_params)}'

    def get_access_token(self, code):
        data = {'client_id': self.consumer_key,
                'client_secret': self.consumer_secret,
                'redirect_uri': self.callback_url,
                'grant_type': 'authorization_code',
                'code': code}
        params = None
        self._strip_empty_keys(data)
        url = self.access_token_url
        if self.access_token_method == 'GET':
            params = data
            data = None
        # TODO: Proper exception handling
        resp = requests.request(self.access_token_method,
                                url,
                                params=params,
                                data=data)
        access_token = None
        if resp.status_code == 200:
            access_token = resp.json()
            access_token['expires_in'] = 2147483647
        if not access_token or 'access_token' not in access_token:
            raise OAuth2Error('Error retrieving access token: %s'
                              % resp.json())
        return access_token
