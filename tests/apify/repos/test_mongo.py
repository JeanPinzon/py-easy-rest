import pytest

from aiounittest import AsyncTestCase
from unittest.mock import Mock

from bson.objectid import ObjectId

from apify.repos.mongo import MongoRepo


class MockMongoCursor():

    async def to_list(self, length):
        pass


class MockMongoCollection():

    async def find_one(self, query):
        pass

    async def insert_one(self, data):
        pass

    async def replace_one(self, query, data):
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

        mocked_collection = Mock(MockMongoCollection)
        mocked_collection.find.return_value = mongo_cursor_mock

        self._mongo_repo.set_db_collection(mocked_collection)

        result = await self._mongo_repo.list(page=0, size=2)

        assert result == expected_documents
        mongo_cursor_mock.to_list.assert_called_once_with(length=2)

    @pytest.mark.asyncio
    async def test_should_create_return_correct_document_id(self):
        mocked_id = "551137c2f9e1fac808a5f572"
        document_to_create = {"name": "Jean"}

        mocked_collection = Mock(MockMongoCollection)
        mocked_collection.insert_one.return_value = MockMongoInsertResult(mocked_id)

        self._mongo_repo.set_db_collection(mocked_collection)

        result = await self._mongo_repo.create(document_to_create)

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
