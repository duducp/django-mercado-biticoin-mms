from django.core.cache import caches
from django.core.cache.backends.base import DEFAULT_TIMEOUT


class LockActiveError(Exception):
    pass


class LockAcquireError(Exception):
    pass


class LockReleaseError(Exception):
    pass


class Lock(object):
    def __init__(self):
        self.active = False


class CacheLock(Lock):
    """
    A context manager to handle a lock status using Django cache

    The active status is True on __enter__ and False on __exit__

    The cache will be deleted on context __exit__
    """

    def __init__(
        self,
        key: str,
        *,
        cache_alias: str = 'default',
        expire=DEFAULT_TIMEOUT,
        raise_exception: bool = True,
        delete_on_exit: bool = True
    ):
        super(CacheLock, self).__init__()
        self._key = key
        self._expire = expire
        self.cache = caches[cache_alias]
        self.raise_exception = raise_exception
        self.delete_on_exit = delete_on_exit

    def __enter__(self):
        try:
            self.active = self.cache.add(self._key, True, self._expire)
        except Exception as e:
            raise LockAcquireError(
                'Could not acquire a lock. Caused by: {}'.format(e)
            )

        if not self.active and self.raise_exception:
            raise LockActiveError('For key {key}'.format(key=self._key))

        return self

    def __exit__(self, *args, **kwargs):
        if self.active and self.delete_on_exit:
            self.delete_cache()

        self.active = False

    def delete_cache(self):
        try:
            self.cache.delete(self._key)
        except Exception as e:
            raise LockReleaseError(
                'Could not release a lock. Caused by: {}'.format(e)
            )
