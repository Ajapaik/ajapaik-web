from ajapaik.settings.default import * # noqa

assert DATABASES  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        'NAME': 'db.sqlite3'
    }
}
