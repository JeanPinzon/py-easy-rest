![Lint](https://github.com/JeanPinzon/py-easy-rest/actions/workflows/python-lint.yml/badge.svg)
![Build and Test](https://github.com/JeanPinzon/py-easy-rest/actions/workflows/python-test.yml/badge.svg)
![Upload Package](https://github.com/JeanPinzon/py-easy-rest/actions/workflows/python-publish.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/py-easy-rest.svg)](https://badge.fury.io/py/py-easy-rest)


# py-easy-rest

It is a lib to create fast and scalable rest apis based on JSON schema in a very simple way. 
It is based on [Sanic](https://sanic.dev) and it has built in extensions to add repositories and caches.


## Getting Started


### How to install

`pip install py-easy-rest`


### Coding your app

> It will use by default an in memory repository. It is not recommended to production applications. 
> The next sections of this documentation will show you ways to integrate your application with Mongo DB and ways to use cache strategies.
> You can also create your own repositories and cache strategies to integrate your app with other technologies.

> `PYRSanicAppBuilder.build` returns a [Sanic App](https://sanic.readthedocs.io/en/stable/sanic/api/app.html), so you can use it to extend and build new things in your app.

```python
#main.py

from py_easy_rest import PYRSanicAppBuilder
from py_easy_rest.service import PYRService


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

service = PYRService(api_config_mock)
sanic_app = PYRSanicAppBuilder.build(api_config_mock, service)

sanic_app.run(
    host='0.0.0.0',
    port=8000,
    debug=True,
)
```


### Running it

`python main.py`

Now you can access `http://localhost:8000/docs` to access your api documentation.


## Integrating with Repositories

It is possible to add a repository to your application persist data into some data base. 
By default it will use a in memory repository, witch is not recommended to production environment.

To create your own repository, you just need to follow the [Repo](https://github.com/JeanPinzon/py-easy-rest/blob/master/py_easy_rest/repos.py) signature and pass it to the App:


```python
service = PYRService(api_config_mock, repo=MyOwnRepo())
```


### Repos ready to use

- [Mongo with Motor client](https://github.com/JeanPinzon/py-easy-rest-mongo-motor-repo)


## Integrating with Cache Strategies

It is possible to add a cache to your application. 
By default it will not use a cache, but you can choice a built in option or create your own cache.

To create your own cache, you just need to follow the [Cache](https://github.com/JeanPinzon/py-easy-rest/blob/master/py_easy_rest/caches.py) signature and pass it to the App:


```python
service = PYRService(api_config_mock, cache=MyOwnCache())
```


### Caches ready to use

- [Redis](https://github.com/JeanPinzon/py-easy-rest-redis-cache)
- [Memory](https://github.com/JeanPinzon/py-easy-rest-memory-cache)


## API Description

#### py_easy_rest.PYRSanicAppBuilder.build()

| Properties             | Required | Default      | Description                              |
|------------------------|----------|--------------|------------------------------------------|
| api_config             | True     | None         | Object with project and schemas config   |
| service                | True     | PYRService() | Service use to handle the operations     |


#### py_easy_rest.services.PYRService()

| Properties             | Required | Default         | Description                              |
|------------------------|----------|-----------------|------------------------------------------|
| api_config             | True     | None            | Object with project and schemas config   |
| repo                   | False    | PYRMemoryRepo() | Repository used as data resource         |
| cache                  | False    | PYRDummyCache() | Cache strategy                           |
| cache_list_seconds_ttl | False    | 10              | TTL to cache the list results in seconds |
| cache_get_seconds_ttl  | False    | 60 * 30         | TTL to cache the get results             |
