from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import TokenExpiredError

from django.core.management.base import BaseCommand
import datetime
import mwoauth
from requests_oauthlib import OAuth1
import requests
import jwt

from ajapaik.ajapaik.models import Photo
from ajapaik.ajapaik.models import User
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp

class Command(BaseCommand):
    help = 'Tests how OAUTH2 refresh_token works'

    def handle(self, *args, **options):
        user = User.objects.filter(username="Zache-test").first()

        app = SocialApp.objects.get(provider='wikimedia-commons')
        consumer_token = {'key': app.client_id, 'secret': app.secret}
        socialToken= SocialToken.objects.get(account__user=user, account__provider='wikimedia-commons')

        client_id = app.client_id
        refresh_url = 'https://commons.wikimedia.org/w/rest.php/oauth2/access_token'
        userinfo_url = 'https://commons.wikimedia.org/w/api.php?action=query&meta=userinfo&format=json'

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

           client = OAuth2Session(client_id, token=token)
           r = client.get(userinfo_url)

        print(r.content)

