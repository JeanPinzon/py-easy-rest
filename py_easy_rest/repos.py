import uuid

"""
Module with repositories to be used connected with api.
"""


class Repo():
    """
    Interface to define contract to repositories.
    All methods raises an <DatabaseError> in case of error.
    """

    async def get(self, slug, id):
        """
        Receives <slug> and <id> and return a dictionary with the result.
        If it not found a data with this <id>, return None.
        """
        raise NotImplementedError

    async def list(self, slug, page=0, size=30):
        """
        Receives <slug>, <page> and <size> and return a object with the result, page and size.
        It's possible to put other properties in this result object too.
        If result is empty, return a empty list.
        """
        raise NotImplementedError

    async def create(self, slug, data, id=None):
        """
        Receives <slug> and <data> with the resource to be saved,
        save it into db, and return the resource id.
        If receive <id>, set this id to the document and return this id.
        """
        raise NotImplementedError

    async def replace(self, slug, id, data):
        """
        Receives <slug> and <data> with the resource to be saved and <id>,
        replace the resource in db.
        """
        raise NotImplementedError

    async def delete(self, slug, id):
        """
        Receives <slug> and <id> and delete it from db.
        """
        raise NotImplementedError


class PYRMemoryRepo(Repo):

    def __init__(self, initial_data=None):
        self._data = {}
        self._data_index = {}

        if initial_data is not None:
            self._data = initial_data

            for key, value in initial_data.items():
                self._data_index[key] = list(self._data[key].keys())

    async def get(self, slug, id):
        self._ensure_slug_exists(slug)
        return self._data[slug].get(id)

    async def list(self, slug, page, size):
        self._ensure_slug_exists(slug)
        page = page or 0
        size = size or 30

        start = page * size
        stop = start + size

        result = self._data_index[slug][start:stop]

        return {
            "result": [self._data[slug][id] for id in result],
            "page": page,
            "size": size,
            "totalCount": len(self._data_index[slug])
        }

    async def create(self, slug, data, id=None):
        self._ensure_slug_exists(slug)

        if id is None:
            id = str(uuid.uuid4())

        data['id'] = id

        if id not in self._data_index[slug]:
            self._data_index[slug].append(id)

        self._data[slug][id] = data

        return id

    async def replace(self, slug, id, data):
        self._ensure_slug_exists(slug)
        if id in self._data_index[slug]:
            data['id'] = id
            self._data[slug][id] = data

    async def delete(self, slug, id):
        self._ensure_slug_exists(slug)
        self._data[slug].pop(id, None)

        if id in self._data_index[slug]:
            self._data_index[slug].remove(id)

    def _ensure_slug_exists(self, slug):
        if not self._data.get(slug):
            self._data[slug] = {}

        if not self._data_index.get(slug):
            self._data_index[slug] = []
