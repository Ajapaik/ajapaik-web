from ajapaik.settings.default import * # noqa

assert DATABASES  # noqa

DATABASES = {
   'default': {
       'ENGINE': 'django.contrib.gis.db.backends.postgis',
       'NAME': 'postgres_test',
       'USER': 'postgres',
       'PASSWORD': 'postgres',
       'HOST': '127.0.0.1',
       'PORT': '5432'
   }
}

SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']
GOOGLE_MAPS_API_KEY = "GOOGLE_MAPS_API_KEY"
