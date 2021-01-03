from ajapaik.settings.default import * # noqa

assert DATABASES  # noqa

DATABASES = {
   'default': {
       'ENGINE': 'django.contrib.gis.db.backends.postgis',
       'NAME': 'postgres_test',
       'USER': 'postgres',
       'PASSWORD': 'postgres',
       'HOST': 'db'
   }
}
