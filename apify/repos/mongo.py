from repos import Repo

class MongoRepo(Repo):
    
    def __init__(self):
        pass

    async def get(self, id):
        # TODO
        return {}

    async def list(self, page, size):
        # TODO
        return [{}]

    async def create(self, data, id=None):
        # TODO
        return id

    async def replace(self, id, data):
        # TODO
        return id

    async def update(self, id, data):
        # TODO
        return id

    async def delete(self, id):
        # TODO
        return id