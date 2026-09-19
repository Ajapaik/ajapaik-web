from django.conf import settings
from django.test.client import RequestFactory

from ajapaik.ajapaik.context_processors import google_maps_api_key, is_user_upload, osm_tile_urls


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


def test_osm_tile_urls():
    rf = RequestFactory()
    get_request = rf.get('/')
    assert osm_tile_urls(get_request) == {
        'osm_tile_url': settings.OSM_TILE_URL,
        'osm_leaflet_tile_url': settings.OSM_LEAFLET_TILE_URL,
    }
