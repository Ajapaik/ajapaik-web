# coding=utf-8

from ajapaik.settings.local import *

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'rephoto_staging',
        'USER': 'rephoto',
        'PASSWORD': 'reph0t0sqluser',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,
        'TEST': {
            'NAME': 'rephoto_staging',
        },
    }
}