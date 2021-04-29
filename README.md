![Lint](https://github.com/JeanPinzon/py-easy-rest/actions/workflows/python-lint.yml/badge.svg)
![Build and Test](https://github.com/JeanPinzon/py-easy-rest/actions/workflows/python-test.yml/badge.svg)
![Upload Package](https://github.com/JeanPinzon/py-easy-rest/actions/workflows/python-publish.yml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/JeanPinzon/py-easy-rest/badge.svg?branch=master)](https://coveralls.io/github/JeanPinzon/py-easy-rest?branch=master)
[![PyPI version](https://badge.fury.io/py/py-easy-rest.svg)](https://badge.fury.io/py/py-easy-rest)

# py-easy-rest

It is a lib to create fast and scalable rest apis based on JSON schema in a very simple way. 
It is based on Sanic and it has built in extensions to add repositories and caches.


## Getting Started

### How to install

`pip install py-easy-rest`


### Coding your app

> It will use by default an in memory repository. It is not recommended to production applications. 
> The next sections of this documentation will show you ways to integrate your application with Mongo DB and ways to use cache strategies.
> You can also create your own repositories and cache strategies to integrate your app with other technologies.

```python
#main.py

from py_easy_rest.server import App


config = {
    "name": "Project Name",
    "schemas": [{
        "name": "Mock",
        "slug": "mock",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
        "required": ["name"],
    }]
}

pyrApp = App(config)

pyrApp.app.run(
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

To create your own repository, you just need to implement our [Repo](https://github.com/JeanPinzon/py-easy-rest/blob/master/py_easy_rest/repos/__init__.py#L16) and pass it to the App: 


```python
pyrApp = App(config, repo=MyOwnRepo())
```

### Mongo Repository

```python
#main.py
from motor.motor_asyncio import AsyncIOMotorClient

from py_easy_rest.server import App
from py_easy_rest.repos.mongo import MongoRepo


config = {
    "name": "Project Name",
    "schemas": [{
        "name": "Mock",
        "slug": "mock",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
        "required": ["name"],
    }]
}

repo = MongoRepo()

pyrApp = App(config, repo=repo)

@pyrApp.app.listener('before_server_start')
def init(app, loop):
    mongo_db_instance = AsyncIOMotorClient("mongodb://localhost:27017/db")
    db = mongo_db_instance.get_default_database()
    collection = db["default"]
    repo.set_db_collection(collection)


pyrApp.app.run(
    host='0.0.0.0',
    port=8000,
    debug=True,
    auto_reload=True,
)
```


## Integrating with Cache Strategies

It is possible to add a cache to your application. 
By default it will not use a cache, but you can choice a built in option or create your own cache.

To create your own cache, you just need to implement our [Cache](https://github.com/JeanPinzon/py-easy-rest/blob/master/py_easy_rest/caches/__init__.py#L16) and pass it to the App: 


```python
pyrApp = App(config, cache=MyOwnCache())
```


### Redis cache

```python
#main.py
from py_easy_rest.server import App
from py_easy_rest.caches.redis import RedisCache


config = {
    "name": "Project Name",
    "schemas": [{
        "name": "Mock",
        "slug": "mock",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
        "required": ["name"],
    }]
}

cache = RedisCache("redis://localhost")

pyrApp = App(config, cache=cache)

pyrApp.app.run(
    host='0.0.0.0',
    port=8000,
    debug=True,
    auto_reload=True,
)
```


### Memory cache

```python
#main.py
from py_easy_rest.server import App
from py_easy_rest.caches.memory import MemoryCache


config = {
    "name": "Project Name",
    "schemas": [{
        "name": "Mock",
        "slug": "mock",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
        "required": ["name"],
    }]
}

cache = MemoryCache()

pyrApp = App(config, cache=cache)

pyrApp.app.run(
    host='0.0.0.0',
    port=8000,
    debug=True,
    auto_reload=True,
)
```

### Middlewares and Listeners

An instance of a `py_easy_rest.server.App` has a property called `app` that is a Sanic app. You can use this property to add middlewares and listeners. 
Take a look at the docs: [Middlewares](https://sanicframework.org/guide/basics/middleware.html#attaching-middleware), 
Take a look at the docs: [Listeners](https://sanicframework.org/guide/basics/listeners.html)

