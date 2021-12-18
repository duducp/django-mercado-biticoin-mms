import os
import sys
from distutils.util import strtobool

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

import dj_database_url
import structlog
from celery.schedules import crontab
from kombu import Exchange, Queue

from project import __version__
from project.core.logging import processors

CORE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_DIR = os.path.dirname(CORE_DIR)
SRC_DIR = os.path.dirname(PROJECT_DIR)
BASE_DIR = os.path.dirname(SRC_DIR)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', '65145e56-8c4f-4434-b451-6e0e3214640e')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(strtobool(os.getenv('DEBUG', 'False')))

WSGI_APPLICATION = 'project.core.wsgi.application'
ROOT_URLCONF = 'project.urls'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(';')

VERSION = __version__
APP_NAME = 'mb-mms-api'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
LOCALE_PATHS = [os.path.join(CORE_DIR, 'locales')]
STATICFILES_DIRS = [os.path.join(CORE_DIR, 'statics')]
MEDIA_ROOT = os.path.join(BASE_DIR, 'medias')
MEDIA_URL = '/medias/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/statics/'

ADMIN_URL = 'admin/'
ADMIN_ENABLED = strtobool(os.getenv('ADMIN_ENABLED', 'true'))
ADMIN_SITE_HEADER = 'Painel de Controle - Play nas Férias'
ADMIN_INDEX_TITLE = 'Administração'
ADMIN_SITE_TITLE = 'Play nas Férias'

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

# Configurations of the django-cid module responsible for generating correlation_id of logs and requests (https://github.com/Polyconseil/django-cid) # noqa
CID_GENERATE = True
CID_CONCATENATE_IDS = True
CID_HEADER = 'X-Correlation-ID'
CID_RESPONSE_HEADER = 'X-Correlation-ID'

# Cors
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

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
                'django.template.context_processors.media',
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
    'corsheaders',
    'django_extensions',
    'django_dbconn_retry',
    'django_celery_beat',
    'cid.apps.CidAppConfig',
]

LOCAL_APPS = [
    'project.ping.apps.PingConfig',
    'project.indicators.mms.apps.MmsConfig',
    'project.tickets.apps.TicketsConfig',
]

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Django middlewares settings
DEFAULT_MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

THIRD_PARTY_MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'cid.middleware.CidMiddleware',
]

LOCAL_MIDDLEWARE = [
    'project.core.middlewares.version_header.VersionHeaderMiddleware',
    'project.core.middlewares.access_logging.AccessLoggingMiddleware',
]

MIDDLEWARE = DEFAULT_MIDDLEWARE + THIRD_PARTY_MIDDLEWARE + LOCAL_MIDDLEWARE

# Redis connection settings (https://github.com/jazzband/django-redis)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv(
            'REDIS_URL', 'redis://127.0.0.1:6379/0'
        ).split(';'),
        'KEY_PREFIX': 'default',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            # 'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            'CONNECTION_POOL_KWARGS': {
                'retry_on_timeout': True
            }
        }
    },
    'lock': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv(
            'REDIS_URL_LOCK', 'redis://127.0.0.1:6379/0'
        ).split(';'),
        'KEY_PREFIX': 'lock',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'retry_on_timeout': True
            }
        }
    },
}
CACHE_LIFETIME = {
    'mms_retrieve': int(os.getenv('CACHE_LIFETIME_MMS_RETRIEVE', 600))
}

# Database django connection settings (https://docs.djangoproject.com/en/3.2/ref/databases) # noqa
DATABASES = {
    'default': dj_database_url.parse(
        url=os.getenv(
            'DATABASE_URL',
            'postgres://postgres:postgres@127.0.0.1:5432/postgres'
        ),
        engine='django.db.backends.postgresql_psycopg2',
        conn_max_age=int(os.getenv(
            'DATABASE_DEFAULT_CONN_MAX_AGE',
            '600'
        )),
        ssl_require=bool(strtobool(os.getenv(
            'DATABASE_DEFAULT_SSL_REQUIRE',
            'False'
        )))
    ),
    'default_read': dj_database_url.parse(
        url=os.getenv(
            'DATABASE_READ_URL',
            'postgres://postgres:postgres@127.0.0.1:5432/postgres'
        ),
        engine='django.db.backends.postgresql_psycopg2',
        conn_max_age=int(os.getenv(
            'DATABASE_DEFAULT_CONN_MAX_AGE',
            '600'
        )),
        ssl_require=bool(strtobool(os.getenv(
            'DATABASE_DEFAULT_SSL_REQUIRE',
            'False'
        )))
    )
}

DATABASE_ROUTERS = ['project.core.databases.DatabaseRouter']

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
        'ignore_if_contains': {
            '()': 'project.core.logging.filters.IgnoreIfContains',
            'substrings': ['/ping'],
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
            'filters': ['ignore_if_contains'],
            'stream': sys.stdout,
        },
    },
    'loggers': {
        '': {
            'handlers': ['stdout'],
            'level': 'INFO',
            'propagate': False,
        },
        'aiohttp': {
            'handlers': ['stdout'],
            'level': 'ERROR',
            'propagate': False,
        },
        'aiohttp-retry': {
            'handlers': ['stdout'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['stdout'],
            'level': 'DEBUG'
        },
        'celery': {
            'handlers': ['stdout'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}

# Configuration of the Structlog module that structures the logs in Json (https://www.structlog.org/en/stable) # noqa
structlog.configure(
    processors=[
        processors.hostname,
        processors.version,
        processors.correlation,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt='iso', key='datetime', utc=True),
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


# Celery (https://docs.celeryproject.org/en/latest/userguide/configuration.html) # noqa
CELERY_TIME_ZONE = TIME_ZONE
CELERY_WORKER_ENABLE_REMOTE_CONTROL = False
CELERY_WORKER_SEND_TASK_EVENTS = False
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_CONTENT_ENCODING = 'utf-8'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')

CELERY_TASK_QUEUES = (
    Queue(
        name='indicator-mms-calculate',
        exchange=Exchange('indicator-mms-calculate', type='direct'),
        routing_key='indicator-mms-calculate',
    ),
    Queue(
        name='indicator-mms-select-pairs',
        exchange=Exchange('indicator-mms-select-pairs', type='direct'),
        routing_key='indicator-mms-select-pairs',
    ),
)

CELERY_BEAT_SCHEDULE = {
    'indicator-mms-select-pairs': {
        'task': (
            'project.indicators.mms.tasks.task_beat_select_pairs_to_mms'
        ),
        'schedule': crontab(
            hour=os.getenv('CELERY_BEAT_HOUR_SELECT_PAIRS_TO_MMS', '*/1')
        )
    },
}


# Settings for applications
SERVICES = {
    'candles': {
        'url': os.getenv('SERVICE_CANDLE_URL', 'http://localhost/'),
        'timeout': float(os.getenv('SERVICE_CANDLE_TIMEOUT', '2')),
        'max_retries': int(os.getenv('SERVICE_CANDLE_MAX_RETRIES', '3')),
    }
}
