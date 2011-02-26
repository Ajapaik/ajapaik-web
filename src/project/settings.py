from global_settings import *
import os
gettext = lambda s: s

ADMINS = (
    ('Kristjan Heinaste', 'kristjan@vigvam.ee'),
    
)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'rephoto',
        'USER': 'rephoto',
        'PASSWORD': 'reph0t0sqluser',
    }
}

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
if 'DJANGO_DEVEL_PORT' in os.environ:
    ADMIN_MEDIA_PREFIX = 'http://server.vigvam.ee:%s/media/admin/' % os.environ['DJANGO_DEVEL_PORT']
else:
    ADMIN_MEDIA_PREFIX = '/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '!$+kvr&xqr8#^y68=v&9^_l7x8gf3%i(dsfdfsdfsdfsdfdsfjt22=@r-5vz5^pne7v'

GOOGLE_MAPS_API_KEY = 'ABQIAAAAaytXfQbnrtMoLxF6JVExNRTfbB6nh1kcJ3l9FzXScOS9StE1RRQmbG8-RLXCXXMJOPMdqTeJvsXUnw'
