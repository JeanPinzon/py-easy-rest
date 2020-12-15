import pytest

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


class TestServer(AsyncTestCase):

    def setUp(self):
        self._mock_repo = Mock(MockRepo)
        self._apify = App(self._mock_repo, "./tests/apify/api-mock.yaml")

    async def _request_api(self, path):
        client = self._apify.app.asgi_client

        request, response = await client.get(path)

        await client.aclose()

        return request, response

    @pytest.mark.asyncio
    async def test_should_get_with_a_not_existent_name_returns_404(self):
        request, response = await self._request_api("/not-existent-name")

        assert response.status == 404

    @pytest.mark.asyncio
    async def test_should_get_schema_returns_200(self):
        expected_schema = {
            "properties": {
                "name": {"type": "string", "required": True},
                "color": {"type": "string", "required": True},
                "year": {"type": "number", "required": True},
            }
        }

        request, response = await self._request_api("/mock/schema")

        assert response.status == 200
        assert response.json() == expected_schema

    @pytest.mark.asyncio
    async def test_should_get_without_id_returns_200_and_a_list_of_resources(self):
        expected_list_of_resources = [
            {"name": "Jean Pinzon"},
            {"name": "Alycio Neto"},
        ]

        self._mock_repo.list.return_value = expected_list_of_resources

        request, response = await self._request_api("/mock")

        assert response.status == 200
        assert response.json() == expected_list_of_resources

    @pytest.mark.asyncio
    async def test_should_get_without_id_pass_pagination_params_to_repo_when_receives_it_as_query_string(self):
        expected_page = 10
        expected_size = 20
        expected_list_of_resources = []

        self._mock_repo.list.return_value = []

        request, response = await self._request_api(f"/mock?page={expected_page}&size={expected_size}")

        assert response.status == 200
        assert response.json() == expected_list_of_resources

        self._mock_repo.list.assert_called_once_with(expected_page, expected_size)
