import pytest
import json

from unittest.mock import Mock
from aiounittest import AsyncTestCase

from py_easy_rest.exceptions import PYRInputNotValidError, PYRNotFoundError
from py_easy_rest.service import PYRService
from py_easy_rest.repos import PYRMemoryRepo
from py_easy_rest.caches import PYRDummyCache


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


class TestPYRService(AsyncTestCase):

    def setUp(self):
        self._repo = Mock(PYRMemoryRepo)
        self._cache = Mock(PYRDummyCache)

        self._cache.get.return_value = None

        self._service = PYRService(
            api_config_mock,
            repo=self._repo,
            cache=self._cache,
        )

    @pytest.mark.asyncio
    async def test_should_list_list_of_resources(self):
        expected_list_of_resources = {
            "result": [
                {"name": "Jean Pinzon"},
                {"name": "Alycio Neto"},
            ],
            "page": 0,
            "size": 30,
            "totalCount": 2,
        }

        self._repo.list.return_value = expected_list_of_resources

        result = await self._service.list("mock", None, None)

        assert result == expected_list_of_resources

        self._repo.list.assert_called_once_with("mock", None, None)

    @pytest.mark.asyncio
    async def test_should_list_returns_a_cached_list(self):
        cached_list = {
            "result": [
                {"name": "Jean Pinzon"},
                {"name": "Alycio Neto"},
            ],
            "page": 0,
            "size": 30,
            "totalCount": 2,
        }

        self._cache.get.return_value = json.dumps(cached_list)

        result = await self._service.list("mock", None, None)

        assert result == cached_list

        self._cache.get.assert_called_once_with("mock.list.page-None.size-None")
        self._repo.list.assert_not_called()

    @pytest.mark.asyncio
    async def test_should_list_with_pagination_returns_a_list_of_resources(self):
        page = 2
        size = 2
        expected_list_of_resources = {
            "result": [
                {"name": "Jean Pinzon"},
                {"name": "Alycio Neto"},
            ],
            "page": page,
            "size": size,
            "totalCount": 2,
        }

        self._repo.list.return_value = expected_list_of_resources

        result = await self._service.list("mock", page, size)

        assert result == expected_list_of_resources

        self._repo.list.assert_called_once_with("mock", page, size)

    @pytest.mark.asyncio
    async def test_should_get_returns_the_correct_resource(self):
        expected_resource = {"name": "Jean Pinzon"}

        self._repo.get.return_value = expected_resource

        result = await self._service.get("mock", "1")

        assert result == expected_resource

    @pytest.mark.asyncio
    async def test_should_get_returns_the_cached_resource(self):
        cached_resource = {"name": "Jean Pinzon"}

        self._cache.get.return_value = json.dumps(cached_resource)

        result = await self._service.get("mock", "6")

        assert result == cached_resource

        self._cache.get.assert_called_once_with("mock.get.id-6")
        self._repo.get.assert_not_called()

    @pytest.mark.asyncio
    async def test_should_get_raises_PYRNotFoundError_if_resource_not_found(self):
        self._repo.get.return_value = None

        with pytest.raises(PYRNotFoundError):
            await self._service.get("mock", "2")

    @pytest.mark.asyncio
    async def test_should_create_runs_correctly_and_returns_the_resource_id(self):
        resource = {"name": "karl"}
        expected_id = "mock-id"

        self._repo.create.return_value = expected_id

        result = await self._service.create("mock", resource)

        assert result == expected_id

        self._repo.create.assert_called_once_with("mock", resource, None)

    @pytest.mark.asyncio
    async def test_should_post_raises_PYRInputNotValidError_when_data_is_not_valid(self):
        with pytest.raises(PYRInputNotValidError):
            await self._service.create("mock", {"name": "karl", "age": "twenty eight"})

        self._repo.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_should_create_with_id_runs_correctly_and_returns_the_resource_id(self):
        resource = {"name": "karl"}
        resource_id = "mock-id"

        self._repo.create.return_value = resource_id

        result = await self._service.create("mock", resource, resource_id)

        assert result == resource_id

        self._repo.create.assert_called_once_with("mock", resource, resource_id)

    @pytest.mark.asyncio
    async def test_should_replace_runs_correctly(self):
        resource = {"name": "karl"}
        resource_id = "mock-id"

        await self._service.replace("mock", resource, resource_id)

        self._repo.replace.assert_called_once_with("mock", resource_id, resource)

    @pytest.mark.asyncio
    async def test_should_replace_raises_PYRNotFoundError_if_resource_not_found(self):
        resource = {"name": "karl"}
        resource_id = "not-found-id-put"

        self._repo.get.return_value = None

        with pytest.raises(PYRNotFoundError):
            await self._service.replace("mock", resource, resource_id)

        self._repo.replace.assert_not_called()

    @pytest.mark.asyncio
    async def test_should_replace_raises_PYRInputNotValidError_when_data_is_not_valid(self):
        resource = {"name": "karl", "age": "twenty eight"}
        resource_id = "mock-id"

        with pytest.raises(PYRInputNotValidError):
            await self._service.replace("mock", resource, resource_id)

        self._repo.replace.assert_not_called()

    @pytest.mark.asyncio
    async def test_should_partial_update_runs_correctly(self):
        resource = {"name": "karl"}
        resource_id = "mock-id"

        self._repo.get.return_value = {"name": "jean"}

        await self._service.partial_update("mock", resource, resource_id)

        self._repo.replace.assert_called_once_with("mock", resource_id, resource)

    @pytest.mark.asyncio
    async def test_should_partial_update_raises_PYRNotFoundError_if_resource_not_found(self):
        resource = {"name": "karl"}
        resource_id = "not-found-id-patch"

        self._repo.get.return_value = None

        with pytest.raises(PYRNotFoundError):
            await self._service.partial_update("mock", resource, resource_id)

        self._repo.replace.assert_not_called()

    @pytest.mark.asyncio
    async def test_should_partial_update_raises_PYRInputNotValidError_when_data_is_not_valid(self):
        resource = {"name": "karl", "age": "twenty eight"}
        resource_id = "mock-id"

        self._repo.get.return_value = {"name": "jean"}

        with pytest.raises(PYRInputNotValidError):
            await self._service.partial_update("mock", resource, resource_id)

        self._repo.replace.assert_not_called()

    @pytest.mark.asyncio
    async def test_should_delete_runs_correctly(self):
        resource_id = "mock-id"

        await self._service.delete("mock", resource_id)

        self._repo.delete.assert_called_once_with("mock", resource_id)

    @pytest.mark.asyncio
    async def test_should_delete_raises_PYRNotFoundError_if_resource_not_found(self):
        resource_id = "not-found-id-delete"

        self._repo.get.return_value = None

        with pytest.raises(PYRNotFoundError):
            await self._service.delete("mock", resource_id)

        self._repo.replace.assert_not_called()
