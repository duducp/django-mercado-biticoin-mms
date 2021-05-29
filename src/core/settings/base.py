import os
import sys
from distutils.util import strtobool

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

import structlog

CORE_DIR = os.path.dirname(os.path.dirname(__file__))
SRC_DIR = os.path.dirname(CORE_DIR)
BASE_DIR = os.path.dirname(SRC_DIR)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', '65145e56-8c4f-4434-b451-6e0e3214640e')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(strtobool(os.getenv('DEBUG', 'False')))

WSGI_APPLICATION = 'core.wsgi.application'
ROOT_URLCONF = 'urls'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(';')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
LOCALE_PATHS = [os.path.join(CORE_DIR, 'locales')]
STATICFILES_DIRS = [os.path.join(CORE_DIR, 'statics')]
MEDIA_ROOT = os.path.join(BASE_DIR, 'medias')
MEDIA_URL = '/medias/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/statics/'

ADMIN_URL = 'admin/'
ADMIN_ENABLED = strtobool(os.getenv('ADMIN_ENABLED', 'true'))
ADMIN_SITE_HEADER = 'Django Administration'
ADMIN_SITE_TITLE = 'MMV'

LOGIN_URL = reverse_lazy('admin:login')
LOGOUT_URL = reverse_lazy('admin:logout')

# Django timezones and languages settings (https://docs.djangoproject.com/en/3.2/ref/settings) # noqa
TIME_ZONE = 'UTC'
USE_TZ = True
USE_L10N = True
USE_I18N = False
LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('pt-br', _('LANGUAGE_PORTUGUESE_BRAZIL')),
    ('en', _('LANGUAGE_ENGLISH')),
]

# Django templates settings (https://docs.djangoproject.com/en/3.2/topics/templates) # noqa
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(CORE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Django apps settings
DEFAULT_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
if ADMIN_ENABLED:
    DEFAULT_APPS.append('django.contrib.admin')

THIRD_PARTY_APPS = [
    'django_extensions',
]

LOCAL_APPS = []

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Django middlewares settings
DEFAULT_MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

THIRD_PARTY_MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

LOCAL_MIDDLEWARE = []

MIDDLEWARE = DEFAULT_MIDDLEWARE + THIRD_PARTY_MIDDLEWARE + LOCAL_MIDDLEWARE

# Database django connection settings (https://docs.djangoproject.com/en/3.2/ref/databases) # noqa
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

# Type default for primary key fields (https://docs.djangoproject.com/en/3.2/topics/db/models/#automatic-primary-key-fields) # noqa
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Password validation (https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators) # noqa
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},  # noqa
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},  # noqa
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},  # noqa
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},  # noqa
]

# Configuring Django logs (https://docs.djangoproject.com/en/3.2/topics/logging) # noqa
# See the Readme in the Log section
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'formatters': {
        'json': {
            '()': structlog.stdlib.ProcessorFormatter,
            'processor': structlog.processors.JSONRenderer(),
        },
    },
    'handlers': {
        'stdout': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
            'filters': [],
            'stream': sys.stdout,
        },
    },
    'loggers': {
        '': {
            'handlers': ['stdout'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['stdout'],
            'level': 'DEBUG'
        }
    }
}

# Configuration of the Structlog module that structures the logs in Json (https://www.structlog.org/en/stable) # noqa
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.ExceptionPrettyPrinter(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    context_class=structlog.threadlocal.wrap_dict(dict),
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
