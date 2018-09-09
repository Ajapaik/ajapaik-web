from allauth.socialaccount.providers.base import AuthAction, ProviderAccount
from allauth.socialaccount.providers.oauth.provider import OAuthProvider


class MediaWikiAccount(ProviderAccount):
    pass


class MediaWikiProvider(OAuthProvider):
    id = 'mediawiki'
    name = 'MediaWiki'
    account_class = MediaWikiAccount

    def get_auth_url(self, request, action):
        return 'https://en.wikipedia.org/w/index.php'

    def get_auth_params(self, request, action):
        return {
            'title': 'Special:OAuth/authorize',
            'oauth_consumer_key': self.get_app(request).client_id
        }

    def extract_uid(self, data):
        return

    def extract_common_fields(self, data):
        return


provider_classes = [MediaWikiProvider]
