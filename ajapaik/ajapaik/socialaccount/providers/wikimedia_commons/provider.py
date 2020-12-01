from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class Scope(object):
    BASIC = 'basic'
    EDITPAGE = 'editpage'
    UPLOADFILE = 'uploadfile'


class WikimediaCommonsAccount(ProviderAccount):
    def to_str(self):
        dflt = super(WikimediaCommonsAccount, self).to_str()
        return self.account.extra_data.get('username', dflt)


class WikimediaCommonsProvider(OAuth2Provider):
    id = 'wikimedia-commons'
    name = 'Wikimedia Commons'
    account_class = WikimediaCommonsAccount

    def get_default_scope(self):
        scope = [Scope.BASIC]
        return scope

    def get_auth_params(self, request, action):
        ret = super(WikimediaCommonsProvider, self).get_auth_params(request, action)
        return ret

    def extract_uid(self, data):
        return str(data['username'])

    def extract_common_fields(self, data):
        return dict(username=data.get('username'))


providers.registry.register(WikimediaCommonsProvider)
