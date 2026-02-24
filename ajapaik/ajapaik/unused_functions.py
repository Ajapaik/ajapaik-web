import requests
from allauth.socialaccount.models import SocialAccount, SocialToken


def upload_photo_to_wikimedia_commons(request, path):
    social_token = None
    if request.user and request.user.profile:
        social_account = SocialAccount.objects.filter(user=request.user).first()
        social_token = SocialToken.objects.filter(account=social_account, expires_at__gt=datetime.date.today()).last()
    if social_token:
        S = requests.Session()
        URL = "https://commons.wikimedia.org/w/api.php"
        FILE_PATH = path

        # Step 1: Retrieve a login token
        PARAMS_1 = {
            "action": "query",
            "meta": "tokens",
            "type": "login",
            "format": "json"
        }

        headers = {
            "Authentication": "Bearer " + social_token.token
        }

        R = S.get(url=URL, params=PARAMS_1, headers=headers)
        DATA = R.json()
        print(DATA)

        LOGIN_TOKEN = DATA["query"]["tokens"]["logintoken"]

        # Step 2: Send a post request to login. Use of main account for login is not
        # supported. Obtain credentials via Special:BotPasswords
        # (https://www.mediawiki.org/wiki/Special:BotPasswords) for lgname & lgpassword
        PARAMS_2 = {
            "action": "login",
            "format": "json",
            "lgtoken": LOGIN_TOKEN
        }

        R = S.post(URL, data=PARAMS_2, headers=headers)
        DATA = R.json()
        print(DATA)

        # Step 3: Obtain a CSRF token
        PARAMS_3 = {
            "action": "query",
            "meta": "tokens",
            "format": "json"
        }

        R = S.get(url=URL, params=PARAMS_3, headers=headers)

        DATA = R.json()
        print(DATA)

        CSRF_TOKEN = DATA["query"]["tokens"]["csrftoken"]

        # Step 4: Post request to upload a file directly
        PARAMS_4 = {
            "action": "upload",
            "filename": "file_1.jpg",
            "format": "json",
            "token": CSRF_TOKEN,
            "ignorewarnings": 1
        }

        FILE = {'file': ('file_1.jpg', open(FILE_PATH, 'rb'), 'multipart/form-data')}

        R = S.post(URL, files=FILE, data=PARAMS_4)
        DATA = R.json()
        print(DATA)
