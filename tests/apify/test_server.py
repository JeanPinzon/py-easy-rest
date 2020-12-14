import pytest

from unittest.mock import Mock
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



@pytest.mark.asyncio
async def test_should_get_schema_returns_200():
    mock_repo = Mock(MockRepo)
    apify = App(mock_repo, "./tests/apify/api-mock.yaml")

    request, response = await apify.app.asgi_client.get('/mock/schema')

    expected_schema = {
        'properties': {
            'name': {'type': 'string', 'required': True},
            'color': {'type': 'string', 'required': True},
            'year': {'type': 'number', 'required': True},
        }
    }

    assert response.status == 200
    assert response.json() == expected_schema


@pytest.mark.asyncio
async def test_should_get_schema_with_a_not_existent_name_returns_404():
    mock_repo = Mock(MockRepo)
    apify = App(mock_repo, "./tests/apify/api-mock.yaml")

    request, response = await apify.app.asgi_client.get('/not-existent-name/schema')

    assert response.status == 404

@pytest.mark.asyncio
async def test_should_get_without_id_returns_200_and_a_list_of_resources():
    mock_repo = Mock(MockRepo)
    mock_repo.list.return_value = []

    apify = App(mock_repo, "./tests/apify/api-mock.yaml")

    request, response = await apify.app.asgi_client.get('/mock')

    assert response.status == 200
