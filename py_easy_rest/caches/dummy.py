from py_easy_rest.caches import Cache


class DummyCache(Cache):

    async def get(self, key):
        return None

    async def delete(self, key):
        return None

    async def set(self, key, value, ttl=None):
        return None
