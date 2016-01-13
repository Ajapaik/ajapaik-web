# coding=utf-8
import os
import sys

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

gettext = lambda s: s

MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DEFER_JAVASCRIPT = False

FRONTPAGE_DEFAULT_PAGE_SIZE = 50
FRONTPAGE_DEFAULT_ALBUM_PAGE_SIZE = 50

DATING_POINTS = 150
DATING_CONFIRMATION_POINTS = 50

CURATOR_FLICKR_ENABLED = False

AJAPAIK_FACEBOOK_LINK = 'http://www.facebook.com/ajapaik'

ABSOLUTE_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
ABSOLUTE_TEMPLATES_PATH = '%s/templates' % ABSOLUTE_PROJECT_ROOT

if not ABSOLUTE_PROJECT_ROOT in sys.path:
    sys.path.insert(0, ABSOLUTE_PROJECT_ROOT)

STATIC_ROOT = '%s/static-collected' % ABSOLUTE_PROJECT_ROOT
MEDIA_ROOT = '%s/media' % ABSOLUTE_PROJECT_ROOT
VANALINNAD_ROOT = '/var/garage/vanalinnad.mooo.com'
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

STATICFILES_DIRS = (
    '%s/project/ajapaik/static' % ABSOLUTE_PROJECT_ROOT,
)

LOCALE_PATHS = (
    '%s/project/ajapaik/locale' % ABSOLUTE_PROJECT_ROOT,
)

ADMINS = (
    ('Name Surname', 'admin@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'prod_database_name',
        'USER': 'prod_user',
        'PASSWORD': 'prod_p@ssword',
        'HOST': 'localhost',
        'PORT': '',
        'CONN_MAX_AGE': 600,
    }
}

FACEBOOK_APP_KEY = ''
FACEBOOK_APP_SECRET = ''

TIME_ZONE = 'Europe/Helsinki'

LANGUAGE_CODE = 'et'

LANGUAGES = (
    ('et', gettext('Estonian')),
    ('en', gettext('English')),
    ('fi', gettext('Finnish')),
)

MODELTRANSLATION_LANGUAGES = ('et', 'en', 'ru', 'fi', 'sv', 'nl', 'de')
MODELTRANSLATION_PREPOPULATE_LANGUAGE = 'et'
MODELTRANSLATION_FALLBACK_LANGUAGES = ('fi', 'sv', 'nl', 'de', 'ru', 'en', 'et')

SITE_ID = 2

USE_I18N = True

USE_L10N = False

USE_TZ = True

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

SECRET_KEY = '!!! paste your own secret key here !!!'

TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
        'admin_tools.template_loaders.Loader',
    )),
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'project.ajapaik.middleware.ForceDefaultLanguageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'mobi.middleware.MobileDetectionMiddleware',
    'project.ajapaik.middleware.SessionBasedLocaleWithRedirectMiddleware',
    'project.ajapaik.user_middleware.UserMiddleware',
)

ROOT_URLCONF = 'project.ajapaik.urls'

WSGI_APPLICATION = 'project.ajapaik.wsgihandler.application'

TEMPLATE_DIRS = (
    ABSOLUTE_TEMPLATES_PATH,
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'project.ajapaik.context_processors.analytics',
    'project.ajapaik.context_processors.is_then_and_now',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': TEMPLATE_CONTEXT_PROCESSORS,
            'loaders': TEMPLATE_LOADERS
        },
        'DIRS': TEMPLATE_DIRS
    },
]

ADMIN_TOOL_APPS = (
    'project.ajapaik',
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
)

CORE_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'autocomplete_light',
    'django.contrib.admin',
    'django.contrib.sitemaps',
    'django.contrib.admindocs',
    'django.contrib.gis',
)

LOCAL_APPS = (

)

EXTERNAL_APPS = (
    'django_extensions',
    'sorl.thumbnail',
    'rest_framework',
    'compressor',
    'modeltranslation',
    'haystack',
    'registration',
    'bootstrap3',
    'django_bootstrap_dynamic_formsets'
)

ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_AUTO_LOGIN = True
REGISTRATION_EMAIL_HTML = False
LOGIN_REDIRECT_URL = 'project.ajapaik.then_and_now_tours.frontpage'
REGISTRATION_FORM = 'project.ajapaik.then_and_now_tours.UserRegistrationForm'

# TODO: Just use one tuple
INSTALLED_APPS = ADMIN_TOOL_APPS + CORE_APPS + LOCAL_APPS + EXTERNAL_APPS

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.1:8983/solr/collection1'
    }
}

AUTHENTICATION_BACKENDS = (
    'project.ajapaik.user_middleware.AuthBackend',
)

AUTH_PROFILE_MODULE = 'project.ajapaik.Profile'

LOGIN_URL = '/admin/'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
    ),
    'EXCEPTION_HANDLER': 'project.ajapaik.api.custom_exception_handler'
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

DEFAULT_FROM_EMAIL = 'info@ajapaik.ee'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

AJAPAIK_VALIMIMOODUL_URL = 'http://ajapaik.ee:8080/ajapaik-service/AjapaikService.json'

API_DEFAULT_NEARBY_PHOTOS_RANGE = 50000
API_DEFAULT_NEARBY_MAX_PHOTOS = 50

THEN_AND_NOW_TOUR_RANDOM_PHOTO_MIN_DIST = 200
THEN_AND_NOW_TOUR_RANDOM_PHOTO_MAX_DIST = 700
THEN_AND_NOW_TOUR_DEFAULT_PHOTO_COUNT = 10

AJAPAIK_BENEFICIARY_NAME = 'MTÜ EESTI FOTOPÄRAND'
AJAPAIK_BENEFICIARY_ACCT = 'EE072200221048847282'