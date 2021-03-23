import pytest

from aiounittest import AsyncTestCase
from datetime import datetime, timedelta

from py_easy_rest.caches.memory import MemoryCache


class TestMemoryCache(AsyncTestCase):

    @pytest.mark.asyncio
    async def test_should_get_None_when_there_is_no_result_with_key(self):
        cache = MemoryCache()

        result = await cache.get("key")

        assert result is None

    @pytest.mark.asyncio
    async def test_should_get_the_correct_value_when_there_is_result_with_key(self):
        cache = MemoryCache(initial_data={
            "key-1": "value-1",
            "key-2": "value-2",
        })

        result = await cache.get("key-1")

        assert result == "value-1"

    @pytest.mark.asyncio
    async def test_should_get_the_correct_value_when_there_is_result_with_key_and_it_is_not_expired(self):
        cache = MemoryCache(
            initial_data={
                "key-1": "value-1",
                "key-2": "value-2",
            },
            initial_expire_data={
                "key-1": datetime.now() + timedelta(seconds=6)
            }
        )

        result = await cache.get("key-1")

        assert result == "value-1"

    @pytest.mark.asyncio
    async def test_should_get_None_when_there_is_result_with_key_and_it_is_expired(self):
        cache = MemoryCache(
            initial_data={
                "key-1": "value-1",
                "key-2": "value-2",
            },
            initial_expire_data={
                "key-1": datetime.now() + timedelta(seconds=-6)
            }
        )

        result = await cache.get("key-1")

        assert result is None

    @pytest.mark.asyncio
    async def test_should_delete_data_correctly(self):
        cache = MemoryCache(
            initial_data={
                "key-1": "value-1",
                "key-2": "value-2",
            },
        )

        await cache.delete("key-1")

        result = await cache.get("key-1")

        assert result is None

    @pytest.mark.asyncio
    async def test_should_delete_do_nothing_when_there_is_no_result_with_key(self):
        cache = MemoryCache(
            initial_data={
                "key-1": "value-1",
                "key-2": "value-2",
            },
        )

        await cache.delete("key-2")

        result = await cache.get("key-2")

        assert result is None

    @pytest.mark.asyncio
    async def test_should_set_correctly(self):
        cache = MemoryCache()

        await cache.set("key", "value")

        result = await cache.get("key")

        assert result == "value"

    @pytest.mark.asyncio
    async def test_should_set_with_ttl_correctly(self):
        cache = MemoryCache()

        await cache.set("key", "value", 10)

        result = await cache.get("key")

        assert result == "value"
