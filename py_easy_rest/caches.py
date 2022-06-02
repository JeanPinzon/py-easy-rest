"""
Module with cache providers to be used connected with api.
"""


class Cache():
    """
    Interface to define contract to cache providers.
    All methods raises an <CacheError> in case of error.
    """

    async def get(self, key):
        """
        Receives <key> and return a string with the result.
        If it not found a data with this <key>, return None.
        """
        raise NotImplementedError

    async def delete(self, key):
        """
        Receives <key> and delete it from cache.
        """
        raise NotImplementedError

    async def set(self, key, value, ttl=None):
        """
        Receives <key> and <value> and set it into cache.
        If it receives a <ttl>, the value is set with it.
        <ttl> is the time to the cache expires in seconds.
        """
        raise NotImplementedError


class PYRDummyCache(Cache):

    async def get(self, key):
        return None

    async def delete(self, key):
        return None

    async def set(self, key, value, ttl=None):
        return None
