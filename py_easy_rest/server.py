import json

from jsonschema import Draft7Validator
from sanic import Sanic, response
from sanic_ext import Extend, openapi
from sanic.log import logger

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
        cors_origins="*",
    ):
        self._repo = repo
        self._api_config = api_config
        self._cache = cache
        self._cache_list_seconds_ttl = cache_list_seconds_ttl
        self._cache_get_seconds_ttl = cache_get_seconds_ttl

        self._schemas = self._api_config["schemas"]

        self.app = Sanic(self._api_config["name"])

        self.app.error_handler.add(PYRApplicationError, App._handle_app_error)

        for schema in self._schemas:
            self._define_routes(schema)

        self.app.config.CORS_ORIGINS = cors_origins
        self.app.config.OAS_UI_DEFAULT = "swagger"

        Extend(self.app)

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
        enabled_handlers = schema.get('enabled_handlers', [
            "list",
            "create",
            "get",
            "replace",
            "partial_update",
            "delete",
        ])

        @self.app.get(f"/{slug}/schema")
        @openapi.tag(name)
        @openapi.summary("Get JSON Schema")
        @openapi.description("Route to get the api JSON Schema.")
        @openapi.response(200, {"application/json": None}, "Success to get JSON Schema.")
        async def _get_schema(request):
            return response.json(schema, dumps=json_dumps)

        if "list" in enabled_handlers:
            @self.app.get(f"/{slug}")
            @openapi.tag(name)
            @openapi.summary("List entities")
            @openapi.description(
                "Route to list entities. "
                "You can use the parameters page and size. Default values: page=0, size=30."
            )
            @openapi.response(200, {"application/json": []}, "Success to list entities.")
            @openapi.response(500, {"application/json": None}, "Internal server error.")
            @openapi.parameter("page", int, "query")
            @openapi.parameter("size", int, "query")
            async def _list(request):
                page = get_query_string_arg(request.args, "page")
                size = get_query_string_arg(request.args, "size")

                if page is not None:
                    page = int(page)

                if size is not None:
                    size = int(size)

                cache_key = f"{slug}.list.page-{page}.size-{size}"

                cached = await self._cache.get(cache_key)

                if cached is not None:
                    logger.info(f"Found cache result with key {cache_key}")
                    result = json.loads(cached)
                    return response.json(result, dumps=json_dumps)

                logger.info(f"Not found cache result with key {cache_key}")

                result = await self._repo.list(slug, page, size)

                await self._cache.set(cache_key, json_dumps(result), ttl=self._cache_list_seconds_ttl)

                return response.json(result, dumps=json_dumps)

        if "create" in enabled_handlers:
            @self.app.post(f"/{slug}")
            @self.app.post(f"/{slug}/<id>")
            @openapi.tag(name)
            @openapi.summary("Create a new entity")
            @openapi.description(
                "Route to create a new entity. "
                "Take a look at the schema route to know what properties you must send."
            )
            @openapi.response(201, {"application/json": None}, "Success to create a new entity.")
            @openapi.response(400, {"application/json": None}, "Validation error.")
            @openapi.response(500, {"application/json": None}, "Internal server error.")
            @openapi.parameter("id", required=False, allowEmptyValue=True, location="path")
            @openapi.body({"application/json": {}})
            async def _post(request, id=None):
                errors = self._validate(request.json, schema)

                if errors:
                    return response.json({"errors": errors}, status=400, dumps=json_dumps)

                resource_id = await self._repo.create(slug, request.json, id)

                if id:
                    cache_key = f"{slug}.get.id-{id}"
                    await self._cache.delete(cache_key)

                return response.json({"id": resource_id}, status=201, dumps=json_dumps)

        if "get" in enabled_handlers:
            @self.app.get(f"/{slug}/<id>")
            @openapi.tag(name)
            @openapi.summary("Get a entity by id")
            @openapi.description("Route to get a entity by id.")
            @openapi.response(200, {"application/json": None}, "Success to get the entity.")
            @openapi.response(404, {"application/json": None}, "entity not found.")
            @openapi.response(500, {"application/json": None}, "Internal server error.")
            @openapi.parameter("id", location="path")
            async def _get(request, id):
                cache_key = f"{slug}.get.id-{id}"

                cached = await self._cache.get(cache_key)

                if cached is not None:
                    logger.info(f"Found cache result with key {cache_key}")
                    result = json.loads(cached)
                    return response.json(result, dumps=json_dumps)

                logger.info(f"Not found cache result with key {cache_key}")

                result = await self._repo.get(slug, id)

                if result:
                    await self._cache.set(cache_key, json_dumps(result), ttl=self._cache_get_seconds_ttl)
                    return response.json(result, dumps=json_dumps)

                return response.json({}, status=404, dumps=json_dumps)

        if "replace" in enabled_handlers:
            @self.app.put(f"/{slug}/<id>")
            @openapi.tag(name)
            @openapi.summary("Replace a entity by id")
            @openapi.description(
                "Route to replace a entity. "
                "Take a look at the schema route to know what properties you must send."
            )
            @openapi.response(200, {"application/json": None}, "Success to replace the entity.")
            @openapi.response(400, {"application/json": None}, "Validation error.")
            @openapi.response(500, {"application/json": None}, "Internal server error.")
            @openapi.parameter("id", location="path")
            @openapi.body({"application/json": {}})
            async def _put(request, id):
                existent_doc = await self._repo.get(slug, id)

                if not existent_doc:
                    return response.json({}, status=404, dumps=json_dumps)

                errors = self._validate(request.json, schema)

                if errors:
                    return response.json({"errors": errors}, status=400, dumps=json_dumps)

                await self._repo.replace(slug, id, request.json)

                cache_key = f"{slug}.get.id-{id}"
                await self._cache.delete(cache_key)

                return response.json({}, dumps=json_dumps)

        if "partial_update" in enabled_handlers:
            @self.app.patch(f"/{slug}/<id>")
            @openapi.tag(name)
            @openapi.summary("Partial update a entity by id")
            @openapi.description(
                "Route to partial update a entity. "
                "Take a look at the schema route to know what properties you must send."
            )
            @openapi.response(200, {"application/json": None}, "Success to partial update the entity.")
            @openapi.response(400, {"application/json": None}, "Validation error.")
            @openapi.response(500, {"application/json": None}, "Internal server error.")
            @openapi.parameter("id", location="path")
            @openapi.body({"application/json": {}})
            async def _patch(request, id):
                existent_doc = await self._repo.get(slug, id)

                if not existent_doc:
                    return response.json({}, status=404, dumps=json_dumps)

                doc = merge(request.json, existent_doc)
                doc.pop("_id", None)

                errors = self._validate(doc, schema)

                if errors:
                    return response.json({"errors": errors}, status=400, dumps=json_dumps)

                await self._repo.replace(slug, id, doc)

                cache_key = f"{slug}.get.id-{id}"
                await self._cache.delete(cache_key)

                return response.json({}, dumps=json_dumps)

        if "delete" in enabled_handlers:
            @self.app.delete(f"/{slug}/<id>")
            @openapi.tag(name)
            @openapi.summary("Delere a entity by id")
            @openapi.description("Route to delete a entity.")
            @openapi.response(200, {"application/json": None}, "Success to delete the entity.")
            @openapi.response(500, {"application/json": None}, "Internal server error.")
            @openapi.parameter("id", location="path")
            async def _delete(request, id):
                existent_doc = await self._repo.get(slug, id)

                if not existent_doc:
                    return response.json({}, status=404, dumps=json_dumps)

                await self._repo.delete(slug, id)

                cache_key = f"{slug}.get.id-{id}"
                await self._cache.delete(cache_key)

                return response.json({}, dumps=json_dumps)
