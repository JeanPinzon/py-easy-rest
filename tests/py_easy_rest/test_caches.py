import pytest

from aiounittest import AsyncTestCase

from py_easy_rest.caches import PYRDummyCache


class TestPYRDummyCache(AsyncTestCase):

    def setUp(self):
        self._cache = PYRDummyCache()

    @pytest.mark.asyncio
    async def test_should_get_return_None(self):
        result = await self._cache.get("mock_key")

        assert result is None

    @pytest.mark.asyncio
    async def test_should_delete_return_None(self):
        result = await self._cache.delete("mock_key")

        assert result is None

    @pytest.mark.asyncio
    async def test_should_set_return_None(self):
        result = await self._cache.set("mock_key", "mock_value")

        assert result is None
