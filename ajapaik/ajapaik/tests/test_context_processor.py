from django.conf import settings
from django.test.client import RequestFactory

from ajapaik.ajapaik.context_processors import google_maps_api_key, is_user_upload


def test_google_maps_api_key():
    rf = RequestFactory()
    get_request = rf.get('/')
    assert google_maps_api_key(get_request) == {'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY}


def test_is_user_upload_false():
    rf = RequestFactory()
    get_request = rf.get('/user-upload/')
    assert is_user_upload(get_request) == {'is_user_upload': False}


def test_is_user_upload_true():
    rf = RequestFactory()
    get_request = rf.get('/user-upload/', {'next': 'user-upload'})
    assert is_user_upload(get_request) == {'is_user_upload': True}
