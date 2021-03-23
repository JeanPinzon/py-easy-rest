import pytest

from aiounittest import AsyncTestCase
from unittest.mock import Mock

from bson.objectid import ObjectId

from py_easy_rest.repos.mongo import MongoRepo


class MockMongoCursor():

    def skip(self, skip):
        pass

    def limit(self, limit):
        pass

    async def to_list(self, length):
        pass


class MockMongoCollection():

    async def find_one(self, query):
        pass

    async def insert_one(self, data):
        pass

    async def replace_one(self, query, data):
        pass

    async def delete_one(self, query):
        pass

    def find(self):
        pass


class MockMongoInsertResult():

    def __init__(self, inserted_id):
        self.inserted_id = inserted_id


class TestMongoRepo(AsyncTestCase):

    def setUp(self):
        self._mongo_repo = MongoRepo()

    @pytest.mark.asyncio
    async def test_should_get_return_correct_document(self):
        expected_id = "551137c2f9e1fac808a5f572"
        expected_document = {"_id": expected_id}

        mocked_collection = Mock(MockMongoCollection)
        mocked_collection.find_one.return_value = expected_document

        self._mongo_repo.set_db_collection(mocked_collection)

        result = await self._mongo_repo.get(expected_id)

        assert result == expected_document

    @pytest.mark.asyncio
    async def test_should_list_return_correct_list_of_documents(self):
        expected_documents = [{"name": "Jean"}, {"name": "Alycio"}]

        mongo_cursor_mock = Mock(MockMongoCursor)
        mongo_cursor_mock.to_list.return_value = expected_documents
        mongo_cursor_mock.skip.return_value = mongo_cursor_mock
        mongo_cursor_mock.limit.return_value = mongo_cursor_mock

        mocked_collection = Mock(MockMongoCollection)
        mocked_collection.find.return_value = mongo_cursor_mock

        self._mongo_repo.set_db_collection(mocked_collection)

        result = await self._mongo_repo.list(page=0, size=2)

        assert result == expected_documents

    @pytest.mark.asyncio
    async def test_should_list_paginate_correctly(self):
        expected_documents = []

        mongo_cursor_mock = Mock(MockMongoCursor)
        mongo_cursor_mock.to_list.return_value = expected_documents
        mongo_cursor_mock.skip.return_value = mongo_cursor_mock
        mongo_cursor_mock.limit.return_value = mongo_cursor_mock

        mocked_collection = Mock(MockMongoCollection)
        mocked_collection.find.return_value = mongo_cursor_mock

        self._mongo_repo.set_db_collection(mocked_collection)

        await self._mongo_repo.list(page=3, size=5)

        mongo_cursor_mock.to_list.assert_called_once_with(length=5)
        mongo_cursor_mock.skip.assert_called_once_with(15)
        mongo_cursor_mock.limit.assert_called_once_with(5)

    @pytest.mark.asyncio
    async def test_should_create_and_return_correct_document_id_correctly(self):
        mocked_id = "551137c2f9e1fac808a5f572"
        document_to_create = {"name": "Jean"}

        mocked_collection = Mock(MockMongoCollection)
        mocked_collection.insert_one.return_value = MockMongoInsertResult(mocked_id)

        self._mongo_repo.set_db_collection(mocked_collection)

        result = await self._mongo_repo.create(document_to_create)

        assert result == mocked_id

    @pytest.mark.asyncio
    async def test_should_create_with_id_from_param_correctly(self):
        mocked_id = "551137c2f9e1fac808a5f572"
        document_to_create = {"name": "Jean"}

        mocked_collection = Mock(MockMongoCollection)
        mocked_collection.insert_one.return_value = MockMongoInsertResult(mocked_id)

        self._mongo_repo.set_db_collection(mocked_collection)

        result = await self._mongo_repo.create(document_to_create, mocked_id)

        mocked_collection.insert_one.assert_called_once_with(
            {"name": "Jean", "_id": ObjectId(mocked_id)}
        )

        assert result == mocked_id

    @pytest.mark.asyncio
    async def test_should_create_with_id_from_document_correctly(self):
        mocked_id = "551137c2f9e1fac808a5f572"
        document_to_create = {"name": "Jean", "_id": mocked_id}

        mocked_collection = Mock(MockMongoCollection)
        mocked_collection.insert_one.return_value = MockMongoInsertResult(mocked_id)

        self._mongo_repo.set_db_collection(mocked_collection)

        result = await self._mongo_repo.create(document_to_create)

        mocked_collection.insert_one.assert_called_once_with(document_to_create)

        assert result == mocked_id

    @pytest.mark.asyncio
    async def test_should_replace_document_correctly(self):
        mocked_id = "551137c2f9e1fac808a5f572"
        document_to_replace = {"name": "Jean"}

        mocked_collection = Mock(MockMongoCollection)

        self._mongo_repo.set_db_collection(mocked_collection)

        await self._mongo_repo.replace(mocked_id, document_to_replace)

        mocked_collection.replace_one.assert_called_once_with(
            {'_id': ObjectId(mocked_id)},
            document_to_replace,
        )

    @pytest.mark.asyncio
    async def test_should_delete_document_correctly(self):
        mocked_id = "551137c2f9e1fac808a5f572"

        mocked_collection = Mock(MockMongoCollection)

        self._mongo_repo.set_db_collection(mocked_collection)

        await self._mongo_repo.delete(mocked_id)

        mocked_collection.delete_one.assert_called_once_with(
            {'_id': ObjectId(mocked_id)}
        )
