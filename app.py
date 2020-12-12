from apify.server import App
from apify.repos.mongo import MongoRepo
from apify import settings


if __name__ == '__main__':
    apifyApp = App(MongoRepo())
    apifyApp.app.run(
        host='0.0.0.0', 
        port=8000, 
        debug=settings.DEBUG, 
        auto_reload=settings.AUTO_RELOAD
    )