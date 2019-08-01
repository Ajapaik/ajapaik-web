# coding=utf-8
import os
import sys

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

gettext = lambda s: s

MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'

DEBUG = False

DEFER_JAVASCRIPT = False

FRONTPAGE_DEFAULT_PAGE_SIZE = 50
FRONTPAGE_DEFAULT_ALBUM_PAGE_SIZE = 50

DATING_POINTS = 150
DATING_CONFIRMATION_POINTS = 50

CURATOR_FLICKR_ENABLED = False
CURATOR_EUROPEANA_ENABLED = False

AJAPAIK_FACEBOOK_LINK = 'https://www.facebook.com/ajapaik'

ABSOLUTE_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
ABSOLUTE_TEMPLATES_PATH = '%s/templates' % ABSOLUTE_PROJECT_ROOT

if not ABSOLUTE_PROJECT_ROOT in sys.path:
    sys.path.insert(0, ABSOLUTE_PROJECT_ROOT)

STATIC_ROOT = '%s/static-collected' % ABSOLUTE_PROJECT_ROOT
MEDIA_ROOT = '%s/media' % ABSOLUTE_PROJECT_ROOT
VANALINNAD_ROOT = '/home/ajapaik/vanalinnad.mooo.com'
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

STATICFILES_DIRS = (
    '%s/ajapaik/ajapaik/static' % ABSOLUTE_PROJECT_ROOT,
)

LOCALE_PATHS = (
    '%s/ajapaik/ajapaik/locale' % ABSOLUTE_PROJECT_ROOT,
)

ADMINS = (
    ('Name Surname', 'admin@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db'
    }
}

FACEBOOK_APP_KEY = ''
FACEBOOK_APP_SECRET = ''

TIME_ZONE = 'Europe/Tallinn'

LANGUAGE_CODE = 'et'

LANGUAGES = (
    ('et', gettext('Estonian')),
    ('en', gettext('English')),
    ('fi', gettext('Finnish')),
    ('sv', gettext('Swedish'))
)

MODELTRANSLATION_LANGUAGES = ('et', 'en', 'ru', 'fi', 'sv', 'nl', 'de', 'no')
MODELTRANSLATION_PREPOPULATE_LANGUAGE = 'et'
MODELTRANSLATION_FALLBACK_LANGUAGES = ('fi', 'sv', 'no', 'nl', 'de', 'ru', 'en', 'et')

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

MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'ajapaik.ajapaik.middleware.SubdomainMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'ajapaik.ajapaik.user_middleware.UserMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware'
]

ROOT_URLCONF = 'ajapaik.ajapaik.urls'

SUBDOMAIN_URLCONFS = {
    None: 'ajapaik.ajapaik.urls',
    'opendata': 'ajapaik.ajapaik.urls_opendata'
}

WSGI_APPLICATION = 'wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'context_processors': (
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'ajapaik.ajapaik.context_processors.analytics',
                'ajapaik.ajapaik.context_processors.is_user_upload',
            ),
            'loaders': (
                ('django.template.loaders.cached.Loader', (
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                    'admin_tools.template_loaders.Loader',
                )),
            )
        },
        'DIRS': (
            ABSOLUTE_TEMPLATES_PATH,
            '%s/ajapaik/ajapaik/templates' % ABSOLUTE_PROJECT_ROOT
        )
    },
]

ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_AUTO_LOGIN = True
REGISTRATION_EMAIL_HTML = False
LOGIN_REDIRECT_URL = '/'
REGISTRATION_FORM = 'ajapaik.ajapaik.forms.UserRegistrationForm'

INSTALLED_APPS = (
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
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
    'django_comments_xtd',
    'django_comments',
    'ajapaik.ajapaik',
    'django_extensions',
    'sorl.thumbnail',
    'rest_framework',
    'compressor',
    'modeltranslation',
    'haystack',
    'registration',
    'bootstrap4',
    'django_bootstrap_dynamic_formsets',
    'leaflet',
    'django_celery_beat',
    'ajapaik.ajapaik_face_recognition',
    'ajapaik.ajapaik_object_recognition',
    'django_user_agents',

    # Django allauth and related applications.
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
)

# Note: Allauth login's next-parameter redirection doesn't understand wildcards in ALLOWED_HOSTS.
ALLOWED_HOSTS = ['.ajapaik.ee', '127.0.0.1']

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.1:8983/solr/collection1',
    },
}

AUTHENTICATION_BACKENDS = (
    'ajapaik.ajapaik.user_middleware.AuthBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

AUTH_PROFILE_MODULE = 'ajapaik.ajapaik.Profile'

LOGIN_URL = '/admin/'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'EXCEPTION_HANDLER': 'ajapaik.ajapaik.api.custom_exception_handler',
    'PAGE_SIZE': 10
}

DEFAULT_FROM_EMAIL = 'info@ajapaik.ee'
SERVER_EMAIL = DEFAULT_FROM_EMAIL
# TODO: Use django-mailgun

AJAPAIK_VALIMIMOODUL_URL = 'https://valimimoodul.ajapaik.ee/ajapaik-service/AjapaikService.json'

API_DEFAULT_NEARBY_PHOTOS_RANGE = 50000
API_DEFAULT_NEARBY_MAX_PHOTOS = 50

AJAPAIK_BENEFICIARY_NAME = 'MTÜ EESTI FOTOPÄRAND'
AJAPAIK_BENEFICIARY_ACCT = 'EE072200221048847282'

COMMENTS_APP = 'django_comments_xtd'
COMMENTS_XTD_MAX_THREAD_LEVEL = 1
COMMENTS_XTD_CONFIRM_EMAIL = False
COMMENTS_XTD_FORM_CLASS = 'ajapaik.ajapaik.forms.CommentForm'
COMMENTS_XTD_MODEL = 'ajapaik.ajapaik.models.MyXtdComment'
COMMENTS_XTD_MARKUP_FALLBACK_FILTER = 'markdown'

# FIXME: These break static images
# COMPRESS_CSS_FILTERS = ['compressor.filters.cssmin.rCSSMinFilter']
# COMPRESS_JS_FILTERS = ['compressor.filters.jsmin.JSMinFilter']

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

LEAFLET_CONFIG = {
    'PLUGINS': {
        'leaflet-fullscreen': {
            'css': 'https://api.mapbox.com/mapbox.js/plugins/leaflet-fullscreen/v1.0.1/leaflet.fullscreen.css',
            'js': 'https://api.mapbox.com/mapbox.js/plugins/leaflet-fullscreen/v1.0.1/Leaflet.fullscreen.min.js',
            'auto-include': True,
        },
        'leaflet-rotatedMarker': {
            'js': '/static/js/leaflet.rotatedMarker.js',
            'auto-include': True,
        },
        'leaflet-geometryutil': {
            'js': '/static/js/leaflet.geometryutil.js',
            'auto-include': True,
        },
        'easy-button': {
            'js': '/static/js/leaflet.easy-button.js',
            'auto-include': True,
        }
    }
}

BOT_USERNAME = 'search_engine_user'
BOT_USER_AGENTS = {
    'AhrefsBot',
    'AlphaBot',
    'Applebot',
    'archive.org_bot',
    'Baiduspider',
    'bingbot',
    'BingPreview',
    'BLEXBot',
    'bot@linkfluence.com',
    'Cliqzbot',
    'datagnionbot',
    'Discordbot',
    'DomainStatsBot',
    'DotBot',
    'DuckDuckBot-Https',
    'DuckDuckGo-Favicons-Bot',
    'EarwigBot',
    'ExtLinksBot',
    'Facebot',
    'facebookexternalhit',
    'Gigabot',
    'Gluten Free Crawler',
    'Gogolbot',
    'Googlebot',
    'Googlebot-Image',
    'Googlebot-Video',
    'Jooblebot',
    'linkdexbot',
    'Mail.RU_Bot',
    'MJ12bot',
    'moatbot',
    'MojeekBot',
    'nsrbot',
    'OutclicksBot',
    'Pinterestbot',
    'pustkibot',
    'rogerbot',
    'SafeDNSBot',
    'ScoutJet',
    'SemrushBot',
    'SemrushBot-BA',
    'SEOkicks',
    'SeznamBot',
    'Slackbot',
    'Slackbot-LinkExpanding',
    'Slack-ImgProxy',
    'SMTBot',
    'spbot',
    'SurdotlyBot',
    'trendictionbot0.5.0',
    'TweetmemeBot',
    'Twitterbot',
    'Uptimebot',
    'yacybot',
    'YandexBot',
    'YandexMobileBot',
    'YandexImages',
    'YandexImageResizer',
    'Wget'
}

CELERY_BROKER_URL = 'redis://redis:6379'
CELERY_RESULT_BACKEND = 'redis://redis:6379'

# Since Celery makes us use Redis anyway, use it some more
# CACHES = {
#     'default': {
#         'BACKEND': 'redis_cache.RedisCache',
#         'LOCATION': 'redis:6379',
#         'OPTIONS': {
#             'DB': 1,
#             'PARSER_CLASS': 'redis.connection.HiredisParser',
#             'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
#             'PICKLE_VERSION': -1,
#         },
#     },
# }

GENERAL_INFO_MODAL_CACHE_TTL = 10 * 60

################################################################################
### Django-allauth configuration
################################################################################
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
ACCOUNT_ADAPTER = 'ajapaik.ajapaik.account_adapter.safeUrlAdapter'

# Email login/registration settings.
# This group of settings configured email confirmation obligatory for email
# registered users and optional for user registered with some social account.
ACCOUNT_USER_DISPLAY = lambda user: user.profile.fb_name if (user.profile and user.profile.fb_name) else user.get_full_name()
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = False
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_EMAIL_REQUIRED = False
SOCIALACCOUNT_QUERY_EMAIL = True
# Autologin, after email confirmation, only works when confirming the email
# address immediately after signing up, assuming users didn’t close their
# browser or used some sort of private browsing mode.
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True

ACCOUNT_FORMS = {
    'signup': 'ajapaik.ajapaik.forms.SignupForm',
}

SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': [
            'email',
            'public_profile',
        ],
    },
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'offline',
        }
    },
}
