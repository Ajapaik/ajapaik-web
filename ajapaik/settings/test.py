from ajapaik.settings.local import *

assert DATABASES

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        'NAME': 'db.sqlite3'
    }
}
