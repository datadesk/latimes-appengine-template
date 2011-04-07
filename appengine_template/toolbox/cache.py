# -*- coding: utf-8 -*-
from django.conf import settings
from google.appengine.api import memcache


def get_cache_key(cache_key):
    """
    Returns a cache key with our global namespacing stuff, 
    like the app version id, baked in.
    
    Requires that you add CACHE_VERSION to your Django settings.py file.
    """
    # Bake the current version id in the cache key
    return '%s-%s' % (settings.CACHE_VERSION, cache_key)


def get_cached_response(request, cache_key):
    """
    Returns a cached response, if one exists.
    
    Returns None if it doesn't.
    
    Provide your request object and the cache_key.
    """
    # Hit the cache and see if it already has this key
    cached_data = memcache.get(cache_key)
    # If it does, return the cached data
    if cached_data is not None:
        # (unless we force a reload with the qs)
        if not request.GET.get('force', None):
            # (or unless we're in DEBUG mode)
            if not settings.DEBUG:
                return cached_data
    return None
