import pytest

from aiounittest import AsyncTestCase

from py_easy_rest.repos import PYRMemoryRepo


class TestPYRMemoryRepo(AsyncTestCase):

    @pytest.mark.asyncio
    async def test_should_get_return_correct_document(self):
        repo = PYRMemoryRepo(initial_data={
            "mock": {
                "id-1": {"name": "Alycio", "id": "id-1"},
                "id-2": {"name": "Jean", "id": "id-2"},
            }
        })

        result = await repo.get("mock", "id-2")

        assert result == {"name": "Jean", "id": "id-2"}

    @pytest.mark.asyncio
    async def test_should_list_return_correct_list_of_documents(self):
        repo = PYRMemoryRepo(initial_data={
            "mock": {
                "id-1": {"name": "Alycio", "id": "id-1"},
                "id-2": {"name": "Jean", "id": "id-2"},
            }
        })

        response = await repo.list("mock", page=0, size=2)

        assert response["page"] == 0
        assert response["size"] == 2
        assert response["result"] == [
            {"name": "Alycio", "id": "id-1"},
            {"name": "Jean", "id": "id-2"},
        ]

    @pytest.mark.asyncio
    async def test_should_list_paginate_correctly(self):
        repo = PYRMemoryRepo(initial_data={
            "mock": {
                "id-1": {"name": "Jean", "id": "id-1"},
                "id-2": {"name": "Alycio", "id": "id-2"},
                "id-3": {"name": "Ronaldo", "id": "id-3"},
                "id-4": {"name": "Romario", "id": "id-4"},
            }
        })

        response = await repo.list("mock", page=1, size=2)

        assert response["result"] == [
            {"name": "Ronaldo", "id": "id-3"},
            {"name": "Romario", "id": "id-4"},
        ]

        response = await repo.list("mock", page=0, size=2)

        assert response["result"] == [
            {"name": "Jean", "id": "id-1"},
            {"name": "Alycio", "id": "id-2"},
        ]

        response = await repo.list("mock", page=2, size=1)

        assert response["result"] == [
            {"name": "Ronaldo", "id": "id-3"},
        ]

        response = await repo.list("mock", page=1, size=3)

        assert response["result"] == [
            {"name": "Romario", "id": "id-4"},
        ]

        response = await repo.list("mock", page=2, size=2)

        assert response["result"] == []

    @pytest.mark.asyncio
    async def test_should_create_with_id_from_param_correctly(self):
        repo = PYRMemoryRepo(initial_data={
            "mock": {
                "id-1": {"name": "Alycio", "id": "id-1"},
                "id-2": {"name": "Jean", "id": "id-2"},
            }
        })

        result = await repo.create("mock", {"name": "Ronaldo"}, "id-3")

        assert result == "id-3"

        created_document = await repo.get("mock", "id-3")

        assert created_document == {"name": "Ronaldo", "id": "id-3"}

    @pytest.mark.asyncio
    async def test_should_replace_document_correctly(self):
        repo = PYRMemoryRepo(initial_data={
            "mock": {
                "id-1": {"name": "Jean", "id": "id-1"},
                "id-2": {"name": "Alycio", "id": "id-2"},
            }
        })

        replaced_document = await repo.get("mock", "id-1")

        assert replaced_document == {"name": "Jean", "id": "id-1"}

        await repo.replace("mock", "id-1", {"name": "Ronaldo"})

        replaced_document = await repo.get("mock", "id-1")

        assert replaced_document == {"name": "Ronaldo", "id": "id-1"}

    @pytest.mark.asyncio
    async def test_should_delete_document_correctly(self):
        repo = PYRMemoryRepo(initial_data={
            "mock": {
                "id-1": {"name": "Alycio", "id": "id-1"},
                "id-2": {"name": "Jean", "id": "id-2"},
            }
        })

        document = await repo.get("mock", "id-1")

        assert document == {"name": "Alycio", "id": "id-1"}

        await repo.delete("mock", "id-1")

        document = await repo.get("mock", "id-1")

        assert document is None
