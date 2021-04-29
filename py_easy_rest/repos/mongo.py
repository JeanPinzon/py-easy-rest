from bson.objectid import ObjectId

from py_easy_rest.repos import Repo


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

        result = await cursor.to_list(length=size)

        return {
            "result": result,
            "page": page,
            "size": size,
        }

    async def create(self, data, id=None):
        if id is not None:
            data['_id'] = ObjectId(id)

        result = await self.collection.insert_one(data)

        return result.inserted_id

    async def replace(self, id, data):
        await self.collection.replace_one({'_id': ObjectId(id)}, data)

    async def delete(self, id):
        await self.collection.delete_one({'_id': ObjectId(id)})
