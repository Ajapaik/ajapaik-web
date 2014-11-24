import os

gettext = lambda s: s

MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'

TIME_ZONE = 'UTC'

LANGUAGE_CODE = 'et'

LANGUAGES = (
    ('et', gettext('Estonian')),
    ('en', gettext('English')),
    ('ru', gettext('Russian')),
)

SITE_ID = 1

USE_I18N = True

SIMPLE_AUTOCOMPLETE = {
    'auth.user': {
        'search_field': 'username',
        'threshold': 25,
        'max_items': 10,
        'duplicate_format_function': lambda obj, model, content_type: 'id: %s' % obj.id
    },
    'project.profile': {
       'search_field': 'fb_name'
    },
    'project.photo': {
       'search_field': 'description'
    }
}

INSTALLED_APPS = (
    'filebrowser',
    'django',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.sitemaps',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'south',
    'sorl.thumbnail',
    'media_bundler',
    'rosetta',
    'project',
    'simple_autocomplete',
    'rest_framework',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    # 'django.middleware.gzip.GZipMiddleware',
    #'django.middleware.http.ConditionalGetMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'project.middleware.ForceDefaultLanguageMiddleware',
    'project.middleware.SessionBasedLocaleWithRedirectMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.locale.LocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'project.user_middleware.UserMiddleware',
    'mobi.middleware.MobileDetectionMiddleware'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.i18n",
    "django.core.context_processors.request",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "project.context_processors.analytics",
)

AUTHENTICATION_BACKENDS = (
    'project.user_middleware.AuthBackend',
)

AUTH_PROFILE_MODULE = 'project.Profile'

ROOT_URLCONF = 'project.urls'

TEMPLATE_DIRS = (
    os.path.join(os.path.abspath(os.path.dirname(__file__)), "templates"),
)

FILEBROWSER_DIRECTORY = 'upload/'

MEDIA_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), "media")

STATIC_ROOT = MEDIA_ROOT + '/static'
STATIC_URL = '/static/'

ADMIN_MEDIA_PREFIX = STATIC_URL + "admin/"

MEDIA_URL = '/media/'

# USE_BUNDLES = True
DEFER_JAVASCRIPT = False

MEDIA_BUNDLES = (
    {
        'type': 'javascript',
        'name': 'scripts_combi',
        'path': MEDIA_ROOT + '/js/',
        'url': MEDIA_URL + 'js/',
        'minify': False,
        'files': (
            'jquery-1.8.3.min.js',
            'keyboard_control.js',
            'jquery.tools.min.js',
            'jquery.history.html5.js',
            'bigscreen.min.js',
            'init.js',
        )
    },
    {
        'type': 'css',
        'name': 'styles_combi',
        'path': MEDIA_ROOT + '/gfx/',
        'url': MEDIA_URL + 'gfx/',
        'minify': False,
        'files': (
            'style.css',
        )
    },
)

FILEBROWSER_VERSIONS = {
    'fb_thumb': {'verbose_name': 'Admin Thumbnail', 'width': 60, 'height': 60, 'opts': 'crop upscale'},
    'thumbnail': {'verbose_name': 'Thumbnail (155x101px)', 'width': 155, 'height': 101, 'opts': 'crop'},
    'small': {'verbose_name': 'Small (300px)', 'width': 300, 'height': '', 'opts': ''},
    'big': {'verbose_name': 'Big (800px)', 'width': 800, 'height': '', 'opts': ''},
}

FILEBROWSER_ADMIN_VERSIONS = ['thumbnail', 'small', 'big']

DEFAULT_CITY_ID = 1

LOGIN_URL = "/admin/"

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'],
	'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework.authentication.BasicAuthentication',),
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}