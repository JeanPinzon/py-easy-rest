
import json

from jsonschema import Draft7Validator
from sanic import Sanic, response
from sanic.log import logger
from sanic_openapi import doc, swagger_blueprint

from py_easy_rest import PYRApplicationError
from py_easy_rest.caches.dummy import DummyCache
from py_easy_rest.repos.memory import MemoryRepo
from py_easy_rest.utils.dictionary import merge
from py_easy_rest.utils.json import JSONEncoder
from py_easy_rest.utils.request import get_query_string_arg


json_dumps = JSONEncoder().encode


class App():

    def __init__(
        self,
        api_config,
        repo=MemoryRepo(),
        cache=DummyCache(),
        cache_list_seconds_ttl=10,
        cache_get_seconds_ttl=60 * 30,  # thirty minutes
    ):
        self._repo = repo
        self._api_config = api_config
        self._cache = cache
        self._cache_list_seconds_ttl = cache_list_seconds_ttl
        self._cache_get_seconds_ttl = cache_get_seconds_ttl

        self._schemas = self._api_config["schemas"]

        self.app = Sanic(self._api_config["name"])

        self.app.blueprint(swagger_blueprint)

        self.app.config["API_TITLE"] = self._api_config["name"]

        self.app.error_handler.add(PYRApplicationError, App._handle_app_error)

        for schema in self._schemas:
            self._define_routes(schema)

    @staticmethod
    async def _handle_app_error(request, exception):
        logger.exception(f"Failed to handle request {exception}")
        return response.json({"message": exception.user_message}, status=500, dumps=json_dumps)

    def _validate(self, resource, schema):
        validator = Draft7Validator(schema)

        errors = []

        for error in validator.iter_errors(resource):
            errors.append(error.message)

        if len(errors) > 0:
            return errors

        return None

    def _define_routes(self, schema):
        slug = schema['slug']
        name = schema['name']

        @self.app.get(f"/{slug}/schema")
        @doc.summary("Get JSON Schema")
        @doc.description("Route to get the api JSON Schema.")
        @doc.response(200, None, description="Success to get JSON Schema.")
        async def get_schema(request):
            return response.json(schema, dumps=json_dumps)

        @self.app.get(f"/{slug}")
        @doc.summary(f"List {name}")
        @doc.description(
            f"Route to list all {name}. "
            "You can use the parameters page and size. Default values: page=0, size=30."
        )
        @doc.response(200, None, description=f"Success to list {name}.")
        @doc.response(500, None, description="Internal server error.")
        @doc.consumes(doc.Integer(name="page"), location="query")
        @doc.consumes(doc.Integer(name="size"), location="query")
        @doc.produces(doc.List(doc.Dictionary()))
        async def _list(request):
            page = get_query_string_arg(request.args, "page")
            size = get_query_string_arg(request.args, "size")

            if page is not None:
                page = int(page)

            if size is not None:
                size = int(size)

            cache_key = f"list.page-{page}.size-{size}"

            cached = await self._cache.get(cache_key)

            if cached is not None:
                logger.info(f"Found cache result with key {cache_key}")
                result = json.loads(cached)
                return response.json(result, dumps=json_dumps)

            logger.info(f"Not found cache result with key {cache_key}")

            result = await self._repo.list(page, size)

            await self._cache.set(cache_key, json_dumps(result), ttl=self._cache_list_seconds_ttl)

            return response.json(result, dumps=json_dumps)

        @self.app.post(f"/{slug}")
        @self.app.post(f"/{slug}/<id>")
        @doc.summary(f"Create a new {name}")
        @doc.description(
            f"Route to create a new document of {name}. "
            "Take a look at the schema route to know what properties you must send."
        )
        @doc.response(201, None, description=f"Success to create a new {name} document.")
        @doc.response(400, None, description="Validation error.")
        @doc.response(500, None, description="Internal server error.")
        @doc.consumes(doc.JsonBody({}), location="body")
        async def _post(request, id=None):
            errors = self._validate(request.json, schema)

            if errors:
                return response.json({"errors": errors}, status=400, dumps=json_dumps)

            resource_id = await self._repo.create(request.json, id)

            if id:
                cache_key = f"get.id-{id}"
                await self._cache.delete(cache_key)

            return response.json({"id": resource_id}, status=201, dumps=json_dumps)

        @self.app.get(f"/{slug}/<id>")
        @doc.summary("Get a document by id")
        @doc.description(f"Route to get a {name} document by id.")
        @doc.response(200, None, description="Success to get the document.")
        @doc.response(404, None, description="Document not found.")
        @doc.response(500, None, description="Internal server error.")
        @doc.produces(doc.Dictionary())
        async def _get(request, id):
            cache_key = f"get.id-{id}"

            cached = await self._cache.get(cache_key)

            if cached is not None:
                logger.info(f"Found cache result with key {cache_key}")
                result = json.loads(cached)
                return response.json(result, dumps=json_dumps)

            logger.info(f"Not found cache result with key {cache_key}")

            result = await self._repo.get(id)

            if result:
                await self._cache.set(cache_key, json_dumps(result), ttl=self._cache_get_seconds_ttl)
                return response.json(result, dumps=json_dumps)

            return response.json({}, status=404, dumps=json_dumps)

        @self.app.put(f"/{slug}/<id>")
        @doc.summary("Replace a document by id")
        @doc.description(
            f"Route to replace a document of {name}. "
            "Take a look at the schema route to know what properties you must send."
        )
        @doc.response(200, None, description="Success to replace the document.")
        @doc.response(400, None, description="Validation error.")
        @doc.response(500, None, description="Internal server error.")
        @doc.consumes(doc.JsonBody({}), location="body")
        async def _put(request, id):
            existent_doc = await self._repo.get(id)

            if not existent_doc:
                return response.json({}, status=404, dumps=json_dumps)

            errors = self._validate(request.json, schema)

            if errors:
                return response.json({"errors": errors}, status=400, dumps=json_dumps)

            await self._repo.replace(id, request.json)

            cache_key = f"get.id-{id}"
            await self._cache.delete(cache_key)

            return response.json({}, dumps=json_dumps)

        @self.app.patch(f"/{slug}/<id>")
        @doc.summary("Partial update a document by id")
        @doc.description(
            f"Route to partial update a document of {name}. "
            "Take a look at the schema route to know what properties you must send."
        )
        @doc.response(200, None, description="Success to partial update the document.")
        @doc.response(400, None, description="Validation error.")
        @doc.response(500, None, description="Internal server error.")
        @doc.consumes(doc.JsonBody({}), location="body")
        async def _patch(request, id):
            existent_doc = await self._repo.get(id)

            if not existent_doc:
                return response.json({}, status=404, dumps=json_dumps)

            doc = merge(request.json, existent_doc)
            doc.pop("_id", None)

            errors = self._validate(doc, schema)

            if errors:
                return response.json({"errors": errors}, status=400, dumps=json_dumps)

            await self._repo.replace(id, doc)

            cache_key = f"get.id-{id}"
            await self._cache.delete(cache_key)

            return response.json({}, dumps=json_dumps)

        @self.app.delete(f"/{slug}/<id>")
        @doc.summary("Delere a document by id")
        @doc.description(f"Route to delete a document of {name}.")
        @doc.response(200, None, description="Success to delete the document.")
        @doc.response(500, None, description="Internal server error.")
        async def _delete(request, id):
            existent_doc = await self._repo.get(id)

            if not existent_doc:
                return response.json({}, status=404, dumps=json_dumps)

            await self._repo.delete(id)

            cache_key = f"get.id-{id}"
            await self._cache.delete(cache_key)

            return response.json({}, dumps=json_dumps)
