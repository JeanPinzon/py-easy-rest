from motor.motor_asyncio import AsyncIOMotorClient

from apify.server import App
from apify.repos.mongo import MongoRepo
from apify import settings


if __name__ == '__main__':
    repo = MongoRepo()
    apifyApp = App(repo, "./api.yaml")

    @apifyApp.app.listener('before_server_start')
    def init(sanic, loop):
        mongo_db_instance = AsyncIOMotorClient(apifyApp.db_connection_string)
        db = mongo_db_instance.get_default_database()
        collection = db[apifyApp.db_collection_name]
        repo.set_db_collection(collection)

    apifyApp.app.run(
        host='0.0.0.0',
        port=8000,
        debug=settings.DEBUG,
        auto_reload=settings.AUTO_RELOAD,
    )
