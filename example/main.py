from motor.motor_asyncio import AsyncIOMotorClient

from now_you_rest.server import App
from now_you_rest.repos.mongo import MongoRepo
from now_you_rest.caches.redis import RedisCache


if __name__ == '__main__':
    repo = MongoRepo()
    cache = RedisCache("redis://localhost")

    api_config = {
        "name": "Example REST API",
        "slug": "example-api",
        "schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "properties": {
                "name": {"type": "string"},
                "color": {"type": "string"},
            },
            "required": ["name", "color"],
        }
    }

    nyrApp = App(repo, api_config, cache=cache)

    @nyrApp.app.listener('before_server_start')
    def init(app, loop):
        mongo_db_instance = AsyncIOMotorClient("mongodb://localhost:27017/db")
        db = mongo_db_instance.get_default_database()
        collection = db["default"]
        repo.set_db_collection(collection)

    nyrApp.app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
        auto_reload=True,
    )
