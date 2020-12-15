import pytest

from tests.apify import BaseTestCase


class TestServer(BaseTestCase):

    @pytest.mark.asyncio
    async def test_should_get_with_a_not_existent_name_returns_404(self):
        request, response = await self.get("/not-existent-name")

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

        request, response = await self.get("/mock/schema")

        assert response.status == 200
        assert response.json() == expected_schema

    @pytest.mark.asyncio
    async def test_should_get_without_id_returns_200_and_a_list_of_resources(self):
        expected_list_of_resources = [
            {"name": "Jean Pinzon"},
            {"name": "Alycio Neto"},
        ]

        self._mock_repo.list.return_value = expected_list_of_resources

        request, response = await self.get("/mock")

        assert response.status == 200
        assert response.json() == expected_list_of_resources

    @pytest.mark.asyncio
    async def test_should_get_without_id_pass_pagination_params_to_repo_when_receives_it_as_query_string(self):
        expected_page = 10
        expected_size = 20
        expected_list_of_resources = []

        self._mock_repo.list.return_value = []

        request, response = await self.get(f"/mock?page={expected_page}&size={expected_size}")

        assert response.status == 200
        assert response.json() == expected_list_of_resources

        self._mock_repo.list.assert_called_once_with(expected_page, expected_size)

    @pytest.mark.asyncio
    async def test_should_get_with_id_returns_200_and_a_resource(self):
        expected_resource = {"name": "Jean Pinzon"}

        self._mock_repo.get.return_value = expected_resource

        request, response = await self.get("/mock/1")

        assert response.status == 200
        assert response.json() == expected_resource

    @pytest.mark.asyncio
    async def test_should_get_with_id_returns_404_if_resource_not_found(self):
        expected_resource = None

        self._mock_repo.get.return_value = expected_resource

        request, response = await self.get("/mock/1")

        assert response.status == 404

    @pytest.mark.asyncio
    async def test_should_post_returns_201_and_resource_id(self):
        resource = {"name": "karl"}
        expected_id = 'mock-id'

        self._mock_repo.create.return_value = expected_id

        request, response = await self.post("/mock", resource)

        assert response.status == 201
        assert response.json() == {"id": expected_id}

        self._mock_repo.create.assert_called_once_with(resource, None)

    @pytest.mark.asyncio
    async def test_should_post_with_id_returns_201_and_resource_id(self):
        resource = {"name": "karl"}
        resource_id = 'mock-id'

        self._mock_repo.create.return_value = resource_id

        request, response = await self.post(f"/mock/{resource_id}", resource)

        assert response.status == 201
        assert response.json() == {"id": resource_id}

        self._mock_repo.create.assert_called_once_with(resource, resource_id)
