"Base Cache class."

from django.core.exceptions import ImproperlyConfigured

class InvalidCacheBackendError(ImproperlyConfigured):
    pass

class BaseCache(object):
    def __init__(self, params):
        timeout = params.get('timeout', 300)
        try:
            timeout = int(timeout)
        except (ValueError, TypeError):
            timeout = 300
        self.default_timeout = timeout

    def get(self, key, default=None):
        """
        Fetch a given key from the cache.  If the key does not exist, return
        default, which itself defaults to None.
        """
        raise NotImplementedError

    def set(self, key, value, timeout=None):
        """
        Set a value in the cache.  If timeout is given, that timeout will be
        used for the key; otherwise the default cache timeout will be used.
        """
        raise NotImplementedError

    def delete(self, key):
        """
        Delete a key from the cache, failing silently.
        """
        raise NotImplementedError

    def get_many(self, keys):
        """
        Fetch a bunch of keys from the cache.  For certain backends (memcached,
        pgsql) this can be *much* faster when fetching multiple values.

        Returns a dict mapping each key in keys to its value.  If the given
        key is missing, it will be missing from the response dict.
        """
        d = {}
        for k in keys:
            val = self.get(k)
            if val is not None:
                d[k] = val
        return d

    def has_key(self, key):
        """
        Returns True if the key is in the cache and has not expired.
        """
        return self.get(key) is not None
