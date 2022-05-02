import pytest
import json

from py_easy_rest.repos import DatabaseError

from tests.py_easy_rest import BaseSanicTestCase


class TestServer(BaseSanicTestCase):

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
    async def test_should_get_without_id_returns_200_and_a_list_of_resources(self):
        expected_list_of_resources = [
            {"name": "Jean Pinzon"},
            {"name": "Alycio Neto"},
        ]

        self._mock_repo.list.return_value = expected_list_of_resources

        request, response = await self.request_api("/mock")

        assert response.status == 200
        assert response.json == expected_list_of_resources

        self._mock_repo.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_get_without_id_returns_200_and_a_cached_list(self):
        cached_list = [
            {"name": "Jean Pinzon"},
            {"name": "Alycio Neto"},
        ]

        self._cache.get.return_value = json.dumps(cached_list)

        request, response = await self.request_api("/mock")

        assert response.status == 200
        assert response.json == cached_list

        self._cache.get.assert_called_once_with("mock.list.page-None.size-None")

    @pytest.mark.asyncio
    async def test_should_get_without_id_pass_pagination_params_to_repo_when_receives_it_as_query_string(self):
        expected_page = 30
        expected_size = 20
        expected_list_of_resources = []

        self._mock_repo.list.return_value = []

        request, response = await self.request_api(f"/mock?page={expected_page}&size={expected_size}")

        assert response.status == 200
        assert response.json == expected_list_of_resources

        self._mock_repo.list.assert_called_once_with("mock", expected_page, expected_size)

    @pytest.mark.asyncio
    async def test_should_get_with_id_returns_200_and_a_resource(self):
        expected_resource = {"name": "Jean Pinzon"}

        self._mock_repo.get.return_value = expected_resource

        request, response = await self.request_api("/mock/1")

        assert response.status == 200
        assert response.json == expected_resource

    @pytest.mark.asyncio
    async def test_should_get_with_id_returns_200_and_cached_resource(self):
        cached_resource = {"name": "Jean Pinzon"}

        self._cache.get.return_value = json.dumps(cached_resource)

        request, response = await self.request_api("/mock/6")

        assert response.status == 200
        assert response.json == cached_resource

        self._cache.get.assert_called_once_with("mock.get.id-6")

    @pytest.mark.asyncio
    async def test_should_get_with_id_returns_404_if_resource_not_found(self):
        expected_resource = None

        self._mock_repo.get.return_value = expected_resource

        request, response = await self.request_api("/mock/2")

        assert response.status == 404

    @pytest.mark.asyncio
    async def test_should_post_returns_201_and_resource_id(self):
        resource = {"name": "karl"}
        expected_id = 'mock-id'

        self._mock_repo.create.return_value = expected_id

        request, response = await self.request_api(
            path="/mock",
            method="POST",
            json=resource
        )

        assert response.status == 201
        assert response.json == {"id": expected_id}

        self._mock_repo.create.assert_called_once_with("mock", resource, None)

    @pytest.mark.asyncio
    async def test_should_post_returns_400_and_errors_when_data_is_not_valid(self):
        resource = {"name": "karl", "age": "twenty eight"}
        expected_id = 'mock-id'

        self._mock_repo.create.return_value = expected_id

        request, response = await self.request_api(
            path="/mock",
            method="POST",
            json=resource
        )

        assert response.status == 400
        assert response.json == {"errors": ["'twenty eight' is not of type 'integer'"]}

        self._mock_repo.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_should_post_with_id_returns_201_and_resource_id(self):
        resource = {"name": "karl"}
        resource_id = 'mock-id'

        self._mock_repo.create.return_value = resource_id

        request, response = await self.request_api(
            path=f"/mock/{resource_id}",
            method="POST",
            json=resource
        )

        assert response.status == 201
        assert response.json == {"id": resource_id}

        self._mock_repo.create.assert_called_once_with("mock", resource, resource_id)

    @pytest.mark.asyncio
    async def test_should_put_returns_200(self):
        resource = {"name": "karl"}
        resource_id = 'mock-id'

        request, response = await self.request_api(
            path=f"/mock/{resource_id}",
            method="PUT",
            json=resource
        )

        assert response.status == 200
        assert response.json == {}

        self._mock_repo.replace.assert_called_once_with("mock", resource_id, resource)

    @pytest.mark.asyncio
    async def test_should_put_returns_404(self):
        resource = {"name": "karl"}
        resource_id = 'not-found-id-put'

        self._mock_repo.get.return_value = None

        request, response = await self.request_api(
            path=f"/mock/{resource_id}",
            method="PUT",
            json=resource
        )

        assert response.status == 404
        assert response.json == {}

        self._mock_repo.replace.assert_not_called()

    @pytest.mark.asyncio
    async def test_should_put_returns_400_and_errors_when_data_is_not_valid(self):
        resource = {"name": "karl", "age": "twenty eight"}
        resource_id = 'mock-id'

        request, response = await self.request_api(
            path=f"/mock/{resource_id}",
            method="PUT",
            json=resource
        )

        assert response.status == 400
        assert response.json == {"errors": ["'twenty eight' is not of type 'integer'"]}

        self._mock_repo.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_should_patch_returns_200(self):
        resource = {"name": "karl"}
        resource_id = 'mock-id'

        self._mock_repo.get.return_value = {"name": "jean"}

        request, response = await self.request_api(
            path=f"/mock/{resource_id}",
            method="PATCH",
            json=resource
        )

        assert response.status == 200
        assert response.json == {}

        self._mock_repo.replace.assert_called_once_with("mock", resource_id, resource)

    @pytest.mark.asyncio
    async def test_should_patch_returns_404(self):
        resource = {"name": "karl"}
        resource_id = 'not-found-id-patch'

        self._mock_repo.get.return_value = None

        request, response = await self.request_api(
            path=f"/mock/{resource_id}",
            method="PATCH",
            json=resource
        )

        assert response.status == 404
        assert response.json == {}

        self._mock_repo.replace.assert_not_called()

    @pytest.mark.asyncio
    async def test_should_patch_returns_400_and_errors_when_data_is_not_valid(self):
        resource = {"name": "karl", "age": "twenty eight"}
        resource_id = 'mock-id'

        self._mock_repo.get.return_value = {"name": "jean"}

        request, response = await self.request_api(
            path=f"/mock/{resource_id}",
            method="PATCH",
            json=resource
        )

        assert response.status == 400
        assert response.json == {"errors": ["'twenty eight' is not of type 'integer'"]}

        self._mock_repo.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_should_delete_returns_200(self):
        resource_id = 'mock-id'

        request, response = await self.request_api(
            path=f"/mock/{resource_id}",
            method="DELETE",
        )

        assert response.status == 200
        assert response.json == {}

        self._mock_repo.delete.assert_called_once_with("mock", resource_id)

    @pytest.mark.asyncio
    async def test_should_delete_returns_404(self):
        resource = {"name": "karl"}
        resource_id = 'not-found-id-delete'

        self._mock_repo.get.return_value = None

        request, response = await self.request_api(
            path=f"/mock/{resource_id}",
            method="DELETE",
            json=resource
        )

        assert response.status == 404
        assert response.json == {}

        self._mock_repo.replace.assert_not_called()

    @pytest.mark.asyncio
    async def test_should_request_returns_500_when_it_result_in_a_not_expected_error(self):
        self._mock_repo.list.side_effect = Exception()

        request, response = await self.request_api("/mock?page=321")

        assert response.status == 500

        self._mock_repo.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_request_with_id_returns_500_when_it_result_in_a_not_expected_error(self):
        self._mock_repo.get.side_effect = Exception()

        request, response = await self.request_api("/mock/234")

        assert response.status == 500

    @pytest.mark.asyncio
    async def test_should_request_returns_500_and_message_when_it_result_in_a_db_error(self):
        expected_error_message = "User friendly error message"

        self._mock_repo.list.side_effect = DatabaseError(
            error_message="System error!",
            user_message=expected_error_message
        )

        request, response = await self.request_api("/mock?page=123")

        assert response.status == 500
        assert response.json == {"message": expected_error_message}

        self._mock_repo.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_request_with_id_returns_500_and_message_when_it_result_in_a_db_error(self):
        resource_id = 'mock-id'
        expected_error_message = "User friendly error message"

        self._mock_repo.get.side_effect = DatabaseError(
            error_message="System error!",
            user_message=expected_error_message
        )

        request, response = await self.request_api(f"/mock/{resource_id}")

        assert response.status == 500
        assert response.json == {"message": expected_error_message}

        self._mock_repo.get.assert_called_once_with("mock", resource_id)

    @pytest.mark.asyncio
    async def test_should_disabled_handlers_return_404(self):
        request, response = await self.request_api("/second/1", method="DELETE")

        assert response.status == 404
