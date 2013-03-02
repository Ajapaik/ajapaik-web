import os
gettext = lambda s: s

MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'et'

LANGUAGES = (
    ('en', gettext('English')),
    ('et', gettext('Estonian')),
    ('ru', gettext('Russian')),
    
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

INSTALLED_APPS = (
    #'grappelli',
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
    'filebrowser',
    'media_bundler',
    'django_extensions',
    'project',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    #'django.middleware.gzip.GZipMiddleware',
    #'django.middleware.http.ConditionalGetMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'project.user_middleware.UserMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.i18n",
    "django.core.context_processors.request",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
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

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), "media")

STATIC_ROOT = MEDIA_ROOT + '/static'
STATIC_URL = '/static/'

ADMIN_MEDIA_PREFIX = STATIC_URL + "admin/"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

#USE_BUNDLES = True
DEFER_JAVASCRIPT = False

MEDIA_BUNDLES = (
    {
        'type': 'javascript',
        'name': 'scripts_combi',
        'path': MEDIA_ROOT + '/js/',
        'url': MEDIA_URL + 'js/',
        'minify': False,
        'files': (
            #'jquery-1.5.1.js',
            'jquery-1.8.3.min.js',
            'keyboard_control.js',
            'jquery.tools.min.js',
            'jquery.history.html5.js',
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
