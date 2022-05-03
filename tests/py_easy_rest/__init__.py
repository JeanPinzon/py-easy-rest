from unittest.mock import Mock
from aiounittest import AsyncTestCase
from py_easy_rest.server import App
from py_easy_rest.repos.memory import MemoryRepo
from py_easy_rest.caches.dummy import DummyCache


api_config_mock = {
    "name": "ProjectName",
    "schemas": [{
        "name": "Mock",
        "slug": "mock",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
        "required": ["name"],
    }, {
        "name": "Second api",
        "slug": "second",
        "properties": {"name": {"type": "string"}},
        "enabled_handlers": ["get"]
    }]
}


class BaseSanicTestCase(AsyncTestCase):

    def setUp(self):
        self._mock_repo = Mock(MemoryRepo)
        self._cache = Mock(DummyCache)

        self._cache.get.return_value = None

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
