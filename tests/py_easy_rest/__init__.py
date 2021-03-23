from unittest.mock import Mock
from aiounittest import AsyncTestCase
from py_easy_rest.server import App
from py_easy_rest.repos.memory import MemoryRepo
from py_easy_rest.caches.memory import MemoryCache


api_config_mock = {
    "name": "Mock",
    "slug": "mock",
    "schema": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
        "required": ["name"],
    }
}


class BaseSanicTestCase(AsyncTestCase):

    def setUp(self):
        self._mock_repo = Mock(MemoryRepo)
        self._cache = MemoryCache()
        self._py_easy_rest = App(
            api_config_mock,
            repo=self._mock_repo,
            cache=self._cache,
        )

    async def request_api(self, path, method="GET", json=None):
        client = self._py_easy_rest.app.asgi_client

        request, response = await client.request(method, path, json=json)

        await client.aclose()

        return request, response
