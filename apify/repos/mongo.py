from bson.objectid import ObjectId

from apify.utils.dictionary import merge
from apify.repos import Repo


class MongoRepo(Repo):

    def __init__(self):
        self.collection = None

    def set_db_collection(self, collection):
        self.collection = collection

    async def get(self, id):
        document = await self.collection.find_one({'_id': ObjectId(id)})
        return document

    async def list(self, page, size):
        page = page or 0
        size = size or 30

        cursor = self.collection.find().skip(page * size).limit(size)

        return await cursor.to_list(length=size)

    async def create(self, data, id=None):
        if id is not None:
            data['_id'] = ObjectId(id)
        elif '_id' in data:
            data['_id'] = ObjectId(data['_id'])

        result = await self.collection.insert_one(data)

        return result.inserted_id

    async def replace(self, id, data):
        await self.collection.replace_one({'_id': ObjectId(id)}, data)

    async def update(self, id, data):
        existent_document = await self.get(id)
        await self.replace((id), merge(data, existent_document))

    async def delete(self, id):
        await self.collection.delete_one({'_id': ObjectId(id)})
