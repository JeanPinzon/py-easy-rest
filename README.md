# Now You REST

It is a lib to create fast  and scalable rest apis in a very simple way.

It is builded using Sanic, and it has a repository to Mongo DB. We have plans to add other repositories and middlewares to cache.

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
    def init(nyr, loop):
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


### How to run

Just run your application with `python main.py`. Now you can access `http://localhost:8000/swagger` to read the api documentation.


### Next steps sorted by priority
 
1. Improve exceptions handling
2. Create events strategy to provide integrations
