from .base import *  # noqa

DEBUG = bool(strtobool(os.getenv('DEBUG', 'True')))
