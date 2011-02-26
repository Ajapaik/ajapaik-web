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

# Make this unique, and don't share it with anybody.
SECRET_KEY = '!$+kvr&xqr8#^y68=v&9^_l7x8gf3%i(dsfdfsdfsdfsdfdsfjt22=@r-5vz5^pne7v'

GOOGLE_MAPS_API_KEY = 'ABQIAAAAaytXfQbnrtMoLxF6JVExNRTfbB6nh1kcJ3l9FzXScOS9StE1RRQmbG8-RLXCXXMJOPMdqTeJvsXUnw'
