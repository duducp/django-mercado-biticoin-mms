from .base import *  # noqa

DEBUG = bool(strtobool(os.getenv('DEBUG', 'True')))
DATABASES['default'] = dj_database_url.parse('sqlite://:memory:')

CELERY_TASK_ALWAYS_EAGER = True
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'memory://')
