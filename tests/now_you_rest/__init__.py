from unittest.mock import Mock
from aiounittest import AsyncTestCase
from now_you_rest.server import App
from now_you_rest.repos import Repo


class MockRepo(Repo):

    async def get(self, id):
        pass

    async def list(self, page, size):
        pass

    async def create(self, data, id=None):
        pass

    async def replace(self, id, data):
        pass

    async def update(self, id, data):
        pass

    async def delete(self, id):
        pass


class BaseSanicTestCase(AsyncTestCase):

    def setUp(self):
        self._mock_repo = Mock(MockRepo)
        self._now_you_rest = App(self._mock_repo, "./tests/now_you_rest/api-mock.yaml")

    async def request_api(self, path, method="GET", json=None):
        client = self._now_you_rest.app.asgi_client

        request, response = await client.request(method, path, json=json)

        await client.aclose()

        return request, response
