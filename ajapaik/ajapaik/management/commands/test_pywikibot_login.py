from django.core.management.base import BaseCommand
from ajapaik.ajapaik.models import User
#from ajapaik.ajapaik.wikitext import  upload_own_photo_wikitext
#from ajapaik.ajapaik.mediawiki.mediawiki import upload_file_to_commons, get_random_commons_image, download_tmp_file, remove_tmp_file, get_wikimedia_api_client
from requests import get
import json
import re
import requests
import os
import pywikibot
from pywikibot import config
from pywikibot.site import APISite, BaseSite


from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import TokenExpiredError

class OAuth2Site(APISite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._access_token = None

    def login(self, access_token=None, cookie_only=None):
        self._access_token = access_token

    def _build_oauth_header(self):
        return {'Authorization': f'Bearer {self._access_token}'}

    def _simple_request(self, action, *args, **kwargs):
        req = super()._simple_request(action, *args, **kwargs)
        req.header.update(self._build_oauth_header())
        return req


def get_mediawiki_url(betacommons=False):
    if betacommons:
        return 'https://commons.wikimedia.beta.wmflabs.org'
    else:
        return 'https://commons.wikimedia.org'

def get_wikimedia_api_client(user):
    app = SocialApp.objects.get(provider='wikimedia-commons')
    consumer_token = {'key': app.client_id, 'secret': app.secret}
    socialToken= SocialToken.objects.get(account__user=user, account__provider='wikimedia-commons')
    client_id = app.client_id
    userinfo_url = get_mediawiki_url() + '/w/api.php?format=json&action=query&meta=userinfo&uiprop=blockinfo%7Cgroups%7Crights%7Chasmsg'
    refresh_url = get_mediawiki_url() + '/w/rest.php/oauth2/access_token'

    token = {
        'access_token': socialToken.token,
        'refresh_token': socialToken.token_secret,
        'token_type': 'Bearer',
        'expires_in': '14400',     # initially 3600, need to be updated by you
        'expires_at': 1625606082.1086454
    }

    extra = {
        'client_id': app.client_id,
        'client_secret': app.secret,
    }

    try:
        client = OAuth2Session(client_id, token=token)
        r = client.get(userinfo_url)
    except TokenExpiredError as e:
        token = client.refresh_token(refresh_url, **extra)
        print(token)
        if 'access_token' in token:
            socialToken.token=token["access_token"]
            socialToken.token_secret=token["refresh_token"]
            socialToken.save()
            print("Refreshing token OK")
        else:
            print("Refreshing token failed")
            return False

        client = OAuth2Session(client_id, token=token)
        r = client.get(userinfo_url)
        print(r.json())

    print("---")
#    site = pywikibot.Site('commons', 'commons')
    pywikibot.config.usernames['commons']['commons'] = 'Zache-test'

#    site.consumer_token  = app.client_id
#    site.consumer_secret =  app.secret
#    site.access_token = socialToken.token
#    site.access_secret = socialToken.token_secret
#    site.login()

    # Oauth login information
    pywikibot.config.authenticate['commons.wikimedia.org'] = ( app.client_id, app.secret, socialToken.token, socialToken.token_secret)
    site = OAuth2Site('commons', 'commons')
#    site = pywikibot.Site("commons")

    # Set a dummy username
    socialToken= SocialToken.objects.get(account__user=user, account__provider='wikimedia-commons')
    t=site.login(access_token=token)
    print(t)
    username = site.user()
    print(f'Logged in as: {username}')


    return client



class Command(BaseCommand):
    help = 'Tests how OAUTH2 refresh_token works'

    def handle(self, *args, **options):
        print("1")
        # user: 44387121 = Kimmo
        # user: 47476736 = Zache
        # user: 52134762 = Zache-test
        user = User.objects.filter(pk=52134762).first()
        print("2")

        print(user.first_name, user.last_name)
        print(3)
        client=get_wikimedia_api_client(user)

