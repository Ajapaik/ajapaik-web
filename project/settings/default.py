import os
import sys

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

gettext = lambda s: s

MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DEFER_JAVASCRIPT = False

GRID_VIEW_ENABLED = False
GRID_VIEW_PAGE_SIZE = 25

CURATOR_ENABLED = False
PUBLIC_PHOTO_UPLOAD_ENABLED = False

ABSOLUTE_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
ABSOLUTE_TEMPLATES_PATH = '%s/templates' % ABSOLUTE_PROJECT_ROOT

if not ABSOLUTE_PROJECT_ROOT in sys.path:
    sys.path.insert(0, ABSOLUTE_PROJECT_ROOT)

STATIC_ROOT = '%s/static-collected' % ABSOLUTE_PROJECT_ROOT
MEDIA_ROOT = '%s/media' % ABSOLUTE_PROJECT_ROOT
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

ADMIN_MEDIA_PREFIX = STATIC_URL + "admin/"

STATICFILES_DIRS = (
    '%s/static' % ABSOLUTE_PROJECT_ROOT,
)

LOCALE_PATHS = (
    '%s/project/home/locale' % ABSOLUTE_PROJECT_ROOT,
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
    }
}

FACEBOOK_APP_KEY = ''
FACEBOOK_APP_SECRET = ''

TIME_ZONE = 'Europe/Tallinn'

LANGUAGE_CODE = 'et'

LANGUAGES = (
    ('et', gettext('Estonian')),
    ('en', gettext('English')),
    ('ru', gettext('Russian')),
    ('fi', gettext('Finnish')),
)

MODELTRANSLATION_LANGUAGES = ('et', 'en', 'ru', 'fi', 'sv', 'nl')
MODELTRANSLATION_PREPOPULATE_LANGUAGE = 'et'
MODELTRANSLATION_FALLBACK_LANGUAGES = ('et', 'fi', 'sv', 'nl', 'en', 'ru')

SITE_ID = 1

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
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'mobi.middleware.MobileDetectionMiddleware',
    'project.home.middleware.SessionBasedLocaleWithRedirectMiddleware',
    'project.home.user_middleware.UserMiddleware',
)

ROOT_URLCONF = 'project.urls'

WSGI_APPLICATION = 'project.wsgihandler.application'

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
    "project.home.context_processors.analytics",
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
)

LOCAL_APPS = (
    'project',
    'project.home',
)

INSTALLED_APPS = ADMIN_TOOL_APPS + CORE_APPS + LOCAL_APPS + EXTERNAL_APPS

AUTHENTICATION_BACKENDS = (
    'project.home.user_middleware.AuthBackend',
)

AUTH_PROFILE_MODULE = 'project.Profile'

LOGIN_URL = "/admin/"

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
    ),
    'EXCEPTION_HANDLER': 'project.home.cat.custom_exception_handler'
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

DEFAULT_FROM_EMAIL = 'info@ajapaik.ee'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

AJAPAIK_VALIMIMOODUL_URL = "http://ajapaik.ee:8080/ajapaik-service/AjapaikService.json"

GCM_ENDPOINT = "https://android.googleapis.com/gcm/send"