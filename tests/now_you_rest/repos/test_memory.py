import pytest

from aiounittest import AsyncTestCase

from now_you_rest.repos.memory import MemoryRepo


class TestMemoryRepo(AsyncTestCase):

    @pytest.mark.asyncio
    async def test_should_get_return_correct_document(self):
        repo = MemoryRepo(initial_data={
            "id-1": {"name": "Alycio"},
            "id-2": {"name": "Jean"},
        })

        result = await repo.get("id-2")

        assert result == {"name": "Jean"}

    @pytest.mark.asyncio
    async def test_should_list_return_correct_list_of_documents(self):
        repo = MemoryRepo(initial_data={
            "id-1": {"name": "Jean"},
            "id-2": {"name": "Alycio"},
        })

        result = await repo.list(page=0, size=2)

        assert result == [
            {"name": "Jean"},
            {"name": "Alycio"},
        ]

    @pytest.mark.asyncio
    async def test_should_list_paginate_correctly(self):
        repo = MemoryRepo(initial_data={
            "id-1": {"name": "Jean"},
            "id-2": {"name": "Alycio"},
            "id-3": {"name": "Ronaldo"},
            "id-4": {"name": "Romario"},
        })

        result = await repo.list(page=1, size=2)

        assert result == [
            {"name": "Ronaldo"},
            {"name": "Romario"},
        ]

        result = await repo.list(page=0, size=2)

        assert result == [
            {"name": "Jean"},
            {"name": "Alycio"},
        ]

        result = await repo.list(page=2, size=1)

        assert result == [
            {"name": "Ronaldo"},
        ]

        result = await repo.list(page=1, size=3)

        assert result == [
            {"name": "Romario"},
        ]

        result = await repo.list(page=2, size=2)

        assert result == []

    @pytest.mark.asyncio
    async def test_should_create_with_id_from_param_correctly(self):
        repo = MemoryRepo(initial_data={
            "id-1": {"name": "Jean"},
            "id-2": {"name": "Alycio"},
        })

        result = await repo.create({"name": "Ronaldo"}, "id-3")

        assert result == "id-3"

        created_document = await repo.get("id-3")

        assert created_document == {"name": "Ronaldo"}

    @pytest.mark.asyncio
    async def test_should_replace_document_correctly(self):
        repo = MemoryRepo(initial_data={
            "id-1": {"name": "Jean"},
            "id-2": {"name": "Alycio"},
        })

        replaced_document = await repo.get("id-1")

        assert replaced_document == {"name": "Jean"}

        await repo.replace("id-1", {"name": "Ronaldo"})

        replaced_document = await repo.get("id-1")

        assert replaced_document == {"name": "Ronaldo"}

    @pytest.mark.asyncio
    async def test_should_delete_document_correctly(self):
        repo = MemoryRepo(initial_data={
            "id-1": {"name": "Jean"},
            "id-2": {"name": "Alycio"},
        })

        document = await repo.get("id-1")

        assert document == {"name": "Jean"}

        await repo.delete("id-1")

        document = await repo.get("id-1")

        assert document is None
