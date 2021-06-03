from .base import *  # noqa

DEBUG = bool(strtobool(os.getenv('DEBUG', 'True')))
DATABASES['default'] = dj_database_url.parse('sqlite://:memory:')
