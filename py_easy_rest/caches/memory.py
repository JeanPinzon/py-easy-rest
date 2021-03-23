from datetime import datetime, timedelta

from py_easy_rest.caches import Cache


class MemoryCache(Cache):

    def __init__(self, initial_data={}, initial_expire_data={}):
        self._data = initial_data
        self._when_data_expire = initial_expire_data

    async def get(self, key):
        value = self._data.get(key)

        if value is not None:
            when_data_expire = self._when_data_expire.get(key)

            if when_data_expire and datetime.now() > when_data_expire:
                await self.delete(key)
                return None

            return value

        return None

    async def set(self, key, value, ttl=None):
        self._data[key] = value

        if ttl is not None:
            when_data_expire = datetime.now() + timedelta(seconds=ttl)
            self._when_data_expire[key] = when_data_expire

    async def delete(self, key):
        self._data.pop(key, None)
        self._when_data_expire.pop(key, None)
