import os


class DatabaseRouter:
    """
    A router to control all database operations on models in the
    auth and contenttypes applications
    https://docs.djangoproject.com/en/3.2/topics/db/multi-db/
    """

    def __init__(self):
        self.settings = (
            os.getenv('SIMPLE_SETTINGS') or
            os.getenv('DJANGO_SETTINGS_MODULE')
        )

    def db_for_read(self, model, **hints):
        if self.settings == 'project.core.settings.test':
            return 'default'
        return 'default_read'

    def db_for_write(self, model, **hints):
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True
