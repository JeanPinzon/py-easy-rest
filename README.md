# Now You REST

It is a lib to create fast and scalable rest apis based on JSON schema in a very simple way. 
It is based on Sanic and it has built in extensions to add repositories and caches.


## Getting Started

### How to install

`pip install now-you-rest`


### Coding your app

> It will use by default an in memory repository. It is not recommended to production applications. 
> The next sections of this documentation will show you ways to integrate your application with Mongo DB and ways to use cache strategies.
> You can also create your own repositories and cache strategies to integrate your app with other technologies.

```python
#main.py

from now_you_rest.server import App


config = {
    "name": "Mock",
    "slug": "mock",
    "schema": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
        "required": ["name"],
    }
}

nyrApp = App(config)

nyrApp.app.run(
    host='0.0.0.0',
    port=8000,
    debug=True,
    auto_reload=True,
)
```


### Running it

`python main.py`

Now you can access `http://localhost:8000/swagger` to access your api documentation.


## Integrating with Repositories


It is possible to add a repository to your application persist data into some data base. 
By default it will use a in memory repository, witch is not recommended to production environment.

To create your own repository, you just need to implement our [Repo](https://gitlab.com/JeanPinzon/apify/-/blob/master/now_you_rest/repos/__init__.py#L16) and pass it to the App: 


```python
nyrApp = App(config, repo=MyOwnRepo())
```

### Mongo Repository

```python
#main.py
from motor.motor_asyncio import AsyncIOMotorClient

from now_you_rest.server import App
from now_you_rest.repos.mongo import MongoRepo


config = {
    "name": "Mock",
    "slug": "mock",
    "schema": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
        "required": ["name"],
    }
}

repo = MongoRepo()

nyrApp = App(config, repo=repo)

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
```


## Integrating with Cache Strategies

It is possible to add a cache to your application. 
By default it will not use a cache, but you can choice a built in option or create your own cache.

To create your own cache, you just need to implement our [Cache](https://gitlab.com/JeanPinzon/apify/-/blob/master/now_you_rest/caches/__init__.py#L16) and pass it to the App: 


```python
nyrApp = App(config, cache=MyOwnCache())
```


### Redis cache

```python
#main.py
from now_you_rest.server import App
from now_you_rest.caches.redis import RedisCache


config = {
    "name": "Mock",
    "slug": "mock",
    "schema": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
        "required": ["name"],
    }
}

cache = RedisCache("redis://localhost")

nyrApp = App(config, cache=cache)

nyrApp.app.run(
    host='0.0.0.0',
    port=8000,
    debug=True,
    auto_reload=True,
)
```


### Memory cache

```python
#main.py
from now_you_rest.server import App
from now_you_rest.caches.memory import MemoryCache


config = {
    "name": "Mock",
    "slug": "mock",
    "schema": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
        "required": ["name"],
    }
}

cache = MemoryCache()

nyrApp = App(config, cache=cache)

nyrApp.app.run(
    host='0.0.0.0',
    port=8000,
    debug=True,
    auto_reload=True,
)
```

### Middlewares and Listeners

An instance of a `now_you_rest.server.App` has a property called `app` that is a Sanic app. You can use this property to add middlewares and listeners. 
Take a look at the docs: [Middlewares](https://sanicframework.org/guide/basics/middleware.html#attaching-middleware), 
Take a look at the docs: [Listeners](https://sanicframework.org/guide/basics/listeners.html)

