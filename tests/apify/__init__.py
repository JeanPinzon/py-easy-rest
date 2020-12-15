from unittest.mock import Mock
from aiounittest import AsyncTestCase
from apify.server import App
from apify.repos import Repo


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


class BaseTestCase(AsyncTestCase):

    def setUp(self):
        self._mock_repo = Mock(MockRepo)
        self._apify = App(self._mock_repo, "./tests/apify/api-mock.yaml")

    async def request_api(self, path):
        client = self._apify.app.asgi_client

        request, response = await client.get(path)

        await client.aclose()

        return request, response
