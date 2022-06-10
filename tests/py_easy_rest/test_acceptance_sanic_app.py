import pytest

from unittest.mock import Mock
from aiounittest import AsyncTestCase

from py_easy_rest import PYRSanicAppBuilder
from py_easy_rest.exceptions import PYRInputNotValidError, PYRNotFoundError
from py_easy_rest.service import PYRService


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


class TestAcceptanceSanicApp(AsyncTestCase):

    def setUp(self):
        self._service = Mock(PYRService)
        self._sanic_app = PYRSanicAppBuilder.build(api_config_mock, self._service)

    async def request_api(self, path, method="GET", json=None):
        client = self._sanic_app.asgi_client

        request, response = await client.request(method, path, json=json)

        await client.aclose()

        return request, response

    @pytest.mark.asyncio
    async def test_should_get_with_a_not_existent_name_returns_404(self):
        request, response = await self.request_api("/not-existent-name")

        assert response.status == 404

    @pytest.mark.asyncio
    async def test_should_get_schema_returns_200(self):
        expected_schema = {
            "name": "Mock",
            "slug": "mock",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
            "required": ["name"],
        }

        request, response = await self.request_api("/mock/schema")

        assert response.status == 200
        assert response.json == expected_schema

    @pytest.mark.asyncio
    async def test_should_works_with_multiple_schemas_correctly(self):
        expected_schema = {
            "name": "Second api",
            "slug": "second",
            "properties": {"name": {"type": "string"}},
            "enabled_handlers": ["get"]
        }

        request, response = await self.request_api("/second/schema")

        assert response.status == 200
        assert response.json == expected_schema

    @pytest.mark.asyncio
    async def test_should_list_returns_200_and_the_list_of_resources(self):
        expected_list_of_resources = [
            {"name": "Jean Pinzon"},
            {"name": "Alycio Neto"},
        ]

        self._service.list.return_value = expected_list_of_resources

        request, response = await self.request_api("/mock")

        assert response.status == 200
        assert response.json == expected_list_of_resources

        self._service.list.assert_called_once_with("mock", None, None)

    @pytest.mark.asyncio
    async def test_should_list_with_pagination_returns_200_and_the_list_of_resources(self):
        expected_page = "30"
        expected_size = "20"
        expected_list_of_resources = []

        self._service.list.return_value = []

        request, response = await self.request_api(f"/mock?page={expected_page}&size={expected_size}")

        assert response.status == 200
        assert response.json == expected_list_of_resources

        self._service.list.assert_called_once_with("mock", expected_page, expected_size)

    @pytest.mark.asyncio
    async def test_should_get_returns_200_and_the_correct_resource(self):
        expected_resource = {"name": "Jean Pinzon"}

        self._service.get.return_value = expected_resource

        request, response = await self.request_api("/mock/1")

        assert response.status == 200
        assert response.json == expected_resource

    @pytest.mark.asyncio
    async def test_should_get_returns_404_if_resource_not_found(self):
        self._service.get.side_effect = PYRNotFoundError("Mock 2 not found")

        request, response = await self.request_api("/mock/2")

        assert response.status == 404
        assert response.json == {"message": "Mock 2 not found"}

    @pytest.mark.asyncio
    async def test_should_post_returns_201_and_the_resource_id(self):
        resource = {"name": "karl"}
        expected_id = "mock-id"

        self._service.create.return_value = expected_id

        request, response = await self.request_api(
            path="/mock",
            method="POST",
            json=resource
        )

        assert response.status == 201
        assert response.json == {"id": expected_id}

        self._service.create.assert_called_once_with("mock", resource, None)

    @pytest.mark.asyncio
    async def test_should_post_returns_400_and_errors_when_data_is_not_valid(self):
        resource = {"name": "karl", "age": "twenty eight"}

        self._service.create.side_effect = PYRInputNotValidError(["'twenty eight' is not of type 'integer'"])

        request, response = await self.request_api(
            path="/mock",
            method="POST",
            json=resource
        )

        assert response.status == 400
        assert response.json == {"message": ["'twenty eight' is not of type 'integer'"]}

    @pytest.mark.asyncio
    async def test_should_post_with_id_returns_201_and_resource_id(self):
        resource = {"name": "karl"}
        resource_id = "mock-id"

        self._service.create.return_value = resource_id

        request, response = await self.request_api(
            path=f"/mock/{resource_id}",
            method="POST",
            json=resource
        )

        assert response.status == 201
        assert response.json == {"id": resource_id}

        self._service.create.assert_called_once_with("mock", resource, resource_id)

    @pytest.mark.asyncio
    async def test_should_put_returns_200(self):
        resource = {"name": "karl"}
        resource_id = "mock-id"

        request, response = await self.request_api(
            path=f"/mock/{resource_id}",
            method="PUT",
            json=resource
        )

        assert response.status == 200
        assert response.json == {}

        self._service.replace.assert_called_once_with("mock", resource, resource_id)

    @pytest.mark.asyncio
    async def test_should_put_returns_404(self):
        resource = {"name": "karl"}
        resource_id = "not-found-id-put"

        self._service.replace.side_effect = PYRNotFoundError("mock not-found-id-put not found")

        request, response = await self.request_api(
            path=f"/mock/{resource_id}",
            method="PUT",
            json=resource
        )

        assert response.status == 404
        assert response.json == {"message": "mock not-found-id-put not found"}

    @pytest.mark.asyncio
    async def test_should_put_returns_400_and_errors_when_data_is_not_valid(self):
        resource = {"name": "karl", "age": "twenty eight"}
        resource_id = "mock-id"

        self._service.replace.side_effect = PYRInputNotValidError(["'twenty eight' is not of type 'integer'"])

        request, response = await self.request_api(
            path=f"/mock/{resource_id}",
            method="PUT",
            json=resource
        )

        assert response.status == 400
        assert response.json == {"message": ["'twenty eight' is not of type 'integer'"]}

    @pytest.mark.asyncio
    async def test_should_patch_returns_200(self):
        resource = {"name": "karl"}
        resource_id = "mock-id"

        request, response = await self.request_api(
            path=f"/mock/{resource_id}",
            method="PATCH",
            json=resource
        )

        assert response.status == 200
        assert response.json == {}

        self._service.partial_update.assert_called_once_with("mock", resource, resource_id)

    @pytest.mark.asyncio
    async def test_should_patch_returns_404(self):
        resource = {"name": "karl"}
        resource_id = "not-found-id-patch"

        self._service.partial_update.side_effect = PYRNotFoundError("mock not-found-id-patch not found")

        request, response = await self.request_api(
            path=f"/mock/{resource_id}",
            method="PATCH",
            json=resource
        )

        assert response.status == 404
        assert response.json == {"message": "mock not-found-id-patch not found"}

    @pytest.mark.asyncio
    async def test_should_patch_returns_400_and_errors_when_data_is_not_valid(self):
        resource = {"name": "karl", "age": "twenty eight"}
        resource_id = "mock-id"

        self._service.partial_update.side_effect = PYRInputNotValidError(["'twenty eight' is not of type 'integer'"])

        request, response = await self.request_api(
            path=f"/mock/{resource_id}",
            method="PATCH",
            json=resource
        )

        assert response.status == 400
        assert response.json == {"message": ["'twenty eight' is not of type 'integer'"]}

    @pytest.mark.asyncio
    async def test_should_delete_returns_200(self):
        resource_id = "mock-id"

        request, response = await self.request_api(
            path=f"/mock/{resource_id}",
            method="DELETE",
        )

        assert response.status == 200
        assert response.json == {}

        self._service.delete.assert_called_once_with("mock", resource_id)

    @pytest.mark.asyncio
    async def test_should_delete_returns_404(self):
        resource = {"name": "karl"}
        resource_id = "not-found-id-delete"

        self._service.delete.side_effect = PYRNotFoundError("mock not-found-id-delete not found")

        request, response = await self.request_api(
            path=f"/mock/{resource_id}",
            method="DELETE",
            json=resource
        )

        assert response.status == 404
        assert response.json == {"message": "mock not-found-id-delete not found"}

    @pytest.mark.asyncio
    async def test_should_request_returns_500_and_message_when_it_result_in_a_unexpected_error(self):
        self._service.list.side_effect = Exception()

        request, response = await self.request_api("/mock")

        assert response.status == 500
        assert response.json == {"message": "Internal Server Error"}

        self._service.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_disabled_handlers_return_404(self):
        request, response = await self.request_api("/second/1", method="DELETE")

        assert response.status == 404
