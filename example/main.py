from motor.motor_asyncio import AsyncIOMotorClient

from now_you_rest.server import App
from now_you_rest.repos.mongo import MongoRepo


if __name__ == '__main__':
    repo = MongoRepo()
    nyrApp = App(repo, "./example/api.yaml")

    @nyrApp.app.listener('before_server_start')
    def init(nyr, loop):
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
