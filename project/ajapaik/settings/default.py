import os
import sys

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

gettext = lambda s: s

MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DEFER_JAVASCRIPT = False

FRONTPAGE_DEFAULT_PAGE_SIZE = 50

AJAPAIK_FACEBOOK_LINK = 'http://www.facebook.com/ajapaik'

ABSOLUTE_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
ABSOLUTE_TEMPLATES_PATH = '%s/templates' % ABSOLUTE_PROJECT_ROOT

if not ABSOLUTE_PROJECT_ROOT in sys.path:
    sys.path.insert(0, ABSOLUTE_PROJECT_ROOT)

STATIC_ROOT = '%s/static-collected' % ABSOLUTE_PROJECT_ROOT
MEDIA_ROOT = '%s/media' % ABSOLUTE_PROJECT_ROOT
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

STATICFILES_DIRS = (
    '%s/project/static' % ABSOLUTE_PROJECT_ROOT,
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
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
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
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'project.ajapaik.context_processors.analytics',
)

ADMIN_TOOL_APPS = (
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
    'django.contrib.sitemaps',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.gis',
)

EXTERNAL_APPS = (
    'django_extensions',
    'sorl.thumbnail',
    'rest_framework',
    'compressor',
    'modeltranslation',
    'haystack',
)

LOCAL_APPS = (
    'project.common',
    'project.ajapaik',
)

INSTALLED_APPS = ADMIN_TOOL_APPS + CORE_APPS + LOCAL_APPS + EXTERNAL_APPS

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), '../../whoosh_index'),
    },
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
    'EXCEPTION_HANDLER': 'project.sift.views.custom_exception_handler'
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