from django.conf import settings


def google_maps_api_key(_):
    return {
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    }


def is_user_upload(request):
    ret = False
    if ('HTTP_REFERER' in request.META and 'user-upload' in request.META['HTTP_REFERER']) \
            or ('next' in request.GET and 'user-upload' in request.GET['next']) \
            or ('next' in request.POST and 'user-upload' in request.POST['next']):
        ret = True

    return {
        'is_user_upload': ret
    }


def osm_tile_urls(_):
    is_debug = getattr(settings, 'DEBUG', False)
    default_osm_url = 'https://tile.openstreetmap.de/' if is_debug else 'https://a.tile.openstreetmap.org/'
    default_osm_leaflet_url = 'https://tile.openstreetmap.de/{z}/{x}/{y}.png' if is_debug else 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
    return {
        'osm_tile_url': getattr(settings, 'OSM_TILE_URL', default_osm_url),
        'osm_leaflet_tile_url': getattr(settings, 'OSM_LEAFLET_TILE_URL', default_osm_leaflet_url),
    }
