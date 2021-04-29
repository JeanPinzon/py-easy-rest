from bson.objectid import ObjectId

from py_easy_rest.repos import Repo


class MemoryRepo(Repo):

    def __init__(self, initial_data=None):
        self._data = {}
        self._sorted_data = []

        if initial_data is not None:
            self._data = initial_data
            self._sorted_data = list(initial_data.keys())

    async def get(self, id):
        return self._data.get(id)

    async def list(self, page, size):
        page = page or 0
        size = size or 10

        start = page * size
        stop = start + size

        result = self._sorted_data[start:stop]

        return {
            "result": [self._data[id] for id in result],
            "page": page,
            "size": size,
            "totalCount": len(self._sorted_data)
        }

    async def create(self, data, id=None):
        if id is None:
            id = ObjectId()

        if id not in self._sorted_data:
            self._sorted_data.append(id)

        self._data[id] = data

        return id

    async def replace(self, id, data):
        if id in self._sorted_data:
            self._data[id] = data

    async def delete(self, id):
        self._data.pop(id, None)

        if id in self._sorted_data:
            self._sorted_data.remove(id)
