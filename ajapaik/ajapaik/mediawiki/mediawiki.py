import hashlib
import os

import requests
from allauth.socialaccount.models import SocialToken, SocialApp
from oauthlib.oauth2 import TokenExpiredError
from requests_oauthlib import OAuth2Session


def get_mediawiki_url(betacommons=False):
    if betacommons:
        return 'https://commons.wikimedia.beta.wmflabs.org'
    else:
        return 'https://commons.wikimedia.org'


def download_tmp_file(url):
    user_agent = "Ajapaik.ee OAUTH2 Uploader"
    headers = {'User-Agent': user_agent}

    local_filename = "/tmp/" + hashlib.md5(url.encode('utf-8')).hexdigest() + ".jpg"
    print("Downloading " + local_filename + " " + url)
    r = requests.get(url, headers=headers)
    f = open(local_filename, 'wb')
    for chunk in r.iter_content(chunk_size=512 * 1024):
        if chunk:  # filter out keep-alive new chunks
            f.write(chunk)
    f.close()
    return local_filename


def remove_tmp_file(url):
    local_filename = "/tmp/" + hashlib.md5(url.encode('utf-8')).hexdigest() + ".jpg"
    print("Deleting " + local_filename)
    if os.path.exists(local_filename):
        os.remove(local_filename)


def get_random_commons_image(level):
    ret = {}
    url = 'https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=revisions%7Ccategories%7Cimageinfo&generator=random&rvprop=content&iiprop=timestamp%7Cuser%7Cmediatype%7Cmime%7Curl&grnnamespace=6&grnlimit=1'
    file = requests.get(url)
    data = file.json()
    for page_id in data["query"]["pages"]:
        page = data["query"]["pages"][page_id]
        if page["imageinfo"][0]["mime"] != "image/jpeg":
            if level < 5:
                print("get_random_image() retrying")
                ret = get_random_commons_image(level + 1)
                return ret
            else:
                print("get_random_image() retry failed")
                exit(1)
        ret["title"] = page["title"]
        ret["wikitext"] = page["revisions"][0]["*"]
        ret["mime"] = page["imageinfo"][0]["mime"]
        ret["image_url"] = page["imageinfo"][0]["url"]
        ret["description_url"] = page["imageinfo"][0]["descriptionurl"]

    return ret


def get_wikimedia_api_client(user):
    app = SocialApp.objects.get(provider='wikimedia-commons')
    social_token = SocialToken.objects.get(account__user=user, account__provider='wikimedia-commons')
    client_id = app.client_id
    userinfo_url = get_mediawiki_url() + '/w/api.php?format=json&action=query&meta=userinfo&uiprop=blockinfo%7Cgroups%7Crights%7Chasmsg'
    refresh_url = get_mediawiki_url() + '/w/rest.php/oauth2/access_token'

    token = {
        'access_token': social_token.token,
        'refresh_token': social_token.token_secret,
        'token_type': 'Bearer',
        'expires_in': '14400',  # initially 3600, need to be updated by you
        'expires_at': 1625606082.1086454
    }

    extra = {
        'client_id': app.client_id,
        'client_secret': app.secret,
    }

    client = OAuth2Session(client_id, token=token)
    try:
        client.get(userinfo_url)
    except TokenExpiredError:
        token = client.refresh_token(refresh_url, **extra)
        print(token)
        if 'access_token' in token:
            social_token.token = token["access_token"]
            social_token.token_secret = token["refresh_token"]
            social_token.save(update_fields=['toke', 'token_secret'])
            print("Refreshing token OK")
        else:
            print("Refreshing token failed")
            return False

        client = OAuth2Session(client_id, token=token)
        client.get(userinfo_url)
    return client


def get_csrf_token(client):
    edit_token_url = get_mediawiki_url() + '/w/api.php?action=query&meta=tokens&format=json'
    r = client.get(edit_token_url)
    data = r.json()
    csrf_token = data['query']['tokens']['csrftoken']
    return csrf_token


def upload_file_to_commons(client, source_filename, target_filename, wikitext, comment):
    mediawiki_api_url = get_mediawiki_url() + "/w/api.php"
    csrf_token = get_csrf_token(client)
    upload_payload = {
        'action': 'upload',
        'format': 'json',
        'filename': source_filename,
        'comment': comment,
        'text': wikitext,
        'ignorewarnings': 1,
        'token': csrf_token,
    }
    files = {'file': (target_filename, open(source_filename, 'rb'), 'multipart/form-data')}
    r = client.post(mediawiki_api_url, data=upload_payload, files=files)
    return r
