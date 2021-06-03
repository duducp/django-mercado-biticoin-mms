class DatabaseRouter:
    """
    A router to control all database operations on models in the
    auth and contenttypes applications
    https://docs.djangoproject.com/en/3.2/topics/db/multi-db/
    """

    @staticmethod
    def db_for_read(model, **hints):
        return 'default_read'

    @staticmethod
    def db_for_write(model, **hints):
        return 'default'

    @staticmethod
    def allow_relation(obj1, obj2, **hints):
        return True
