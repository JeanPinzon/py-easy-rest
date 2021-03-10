# Now You REST

It is a lib to create fast and scalable rest apis in a very simple way.

It is builded using Sanic, and it has a repository to Mongo DB and integrations to memory and Redis cache. It is very simple to add new strategies to cache and repositories.

### How to install

`pip install now-you-rest`


### How to use

```python
#main.py

from motor.motor_asyncio import AsyncIOMotorClient

from now_you_rest.server import App
from now_you_rest.repos.mongo import MongoRepo


if __name__ == '__main__':
    repo = MongoRepo()
    nyrApp = App(repo, "./api.yaml")

    @nyrApp.app.listener('before_server_start')
    def init(app, loop):
        mongo_db_instance = AsyncIOMotorClient("mongodb://localhost:27017")
        db = mongo_db_instance.get_default_database()
        collection = db["default"]
        repo.set_db_collection(collection)

    nyrApp.app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
        auto_reload=True,
    )
```

```yaml
name: Example REST API
slug: example-api
db:
  type: mongo
schema:
  properties:
    name:
      type: string
    color:
      type: string
  required:
    - name
    - color

```


### Middlewares and Listeners

A instance of a `now_you_rest.server.App` has a property called `app` that is a Sanic app. You can use this property to add middlewares and listeners. 
Take a look at the docs: [Middlewares](https://sanicframework.org/guide/basics/middleware.html#attaching-middleware), 
Take a look at the docs: [Listeners](https://sanicframework.org/guide/basics/listeners.html)


### How to run

Just run your application with `python main.py`. Now you can access `http://localhost:8000/swagger` to read the api documentation.

