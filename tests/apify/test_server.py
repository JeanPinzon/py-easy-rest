from unittest.mock import MagicMock
from apify.server import App

repoMock = MagicMock()
apify = App(repoMock, "./tests/apify/api-mock.yaml")


async def test_should_get_schema_returns_200():
    request, response = await apify.app.asgi_client.get('/mock/schema')
    assert response.status == 200