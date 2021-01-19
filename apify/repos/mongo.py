from bson.objectid import ObjectId

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
        cursor = self.collection.find()
        return await cursor.to_list(length=size)

    async def create(self, data, id=None):
        # TODO: Create with id
        result = await self.collection.insert_one(data)
        return result.inserted_id

    async def replace(self, id, data):
        await self.collection.replace_one({'_id': ObjectId(id)}, data)

    async def update(self, id, data):
        # TODO
        return id

    async def delete(self, id):
        # TODO
        return id
