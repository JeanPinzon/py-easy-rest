from bson.objectid import ObjectId

from py_easy_rest.repos import Repo


class MongoRepo(Repo):

    def __init__(self):
        self.connection = None

    def set_db_connection(self, connection):
        self.connection = connection

    async def get(self, slug, id):
        document = await self.connection[slug].find_one({'_id': ObjectId(id)})
        return document

    async def list(self, slug, page, size):
        page = page or 0
        size = size or 30

        cursor = self.connection[slug].find().skip(page * size).limit(size)

        result = await cursor.to_list(length=size)

        return {
            "result": result,
            "page": page,
            "size": size,
        }

    async def create(self, slug, data, id=None):
        if id is not None:
            data['_id'] = ObjectId(id)

        result = await self.connection[slug].insert_one(data)

        return result.inserted_id

    async def replace(self, slug, id, data):
        await self.connection[slug].replace_one({'_id': ObjectId(id)}, data)

    async def delete(self, slug, id):
        await self.connection[slug].delete_one({'_id': ObjectId(id)})
