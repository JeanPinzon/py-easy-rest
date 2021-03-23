import aioredis

from py_easy_rest.caches import Cache


class RedisCache(Cache):

    def __init__(self, connection_string):
        self._connection_string = connection_string

    async def get(self, key):
        redis = await aioredis.create_redis_pool(self._connection_string)

        value = await redis.get(key, encoding='utf-8')

        redis.close()
        await redis.wait_closed()

        if value:
            return value

        return None

    async def set(self, key, value, ttl=0):
        redis = await aioredis.create_redis_pool(self._connection_string)

        await redis.set(key, value, expire=ttl)

        redis.close()
        await redis.wait_closed()

    async def delete(self, key):
        redis = await aioredis.create_redis_pool(self._connection_string)

        await redis.delete(key)

        redis.close()
        await redis.wait_closed()
