from default import *

gettext = lambda s: s

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (('Lauri Elias', 'lauri@ajapaik.ee'),)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'rephoto_dev',
        'USER': 'rephoto',
        'PASSWORD': 'reph0t0sqluser',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,
    }
}

SECRET_KEY = '!$+kvr&xqr8#^y68=v&9^_l7x8gf3%i(dsfdfsdfsdfsdfdsfjt22=@r-5vz5^pne7v'

GOOGLE_ANALYTICS_KEY = 'UA-21689048-3'
GOOGLE_API_KEY  = 'AIzaSyC43wIs4RNEMGJp43h_XYA0SBnUL9Jq9S8'

ALLOWED_HOSTS = ['.sift.pics']

if DEBUG:
    # set INTERNAL_IPS to entire local network
    from fnmatch import fnmatch

    class WildcardNetwork(list):
        def __contains__(self, key):
            for address in self:
                if fnmatch(key, address):
                    return True
            return False

    INTERNAL_IPS = WildcardNetwork(['127.0.0.1', '192.168.*.*', '84.50.154.83'])

    # URL that handles the media, static, etc.
    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'

    INSTALLED_APPS += (
        'debug_toolbar',
    )

    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )