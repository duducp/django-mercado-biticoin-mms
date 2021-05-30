from .base import *  # noqa

DATABASES['default'] = dj_database_url.parse('sqlite://:memory:')
