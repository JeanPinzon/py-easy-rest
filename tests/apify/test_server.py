import pytest

from unittest.mock import MagicMock
from apify.server import App


@pytest.mark.asyncio
async def test_should_get_schema_returns_200():
    repoMock = MagicMock()
    apify = App(repoMock, "./tests/apify/api-mock.yaml")

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
