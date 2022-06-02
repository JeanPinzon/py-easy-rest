from sanic import Sanic, response
from sanic_ext import Extend, openapi
from sanic.exceptions import SanicException
from sanic.handlers import ErrorHandler
from sanic.log import logger

from py_easy_rest.exceptions import PYRInputNotValidError, PYRNotFoundError


class PYRSanicAppBuilder():

    @staticmethod
    def build(
        api_config,
        service,
    ):
        schemas = api_config["schemas"]

        app = Sanic(api_config["name"])

        service.set_logger(logger)

        for schema in schemas:
            PYRSanicAppBuilder._define_routes(schema, app, service)

        app.error_handler = CustomErrorHandler()

        Extend(app)

        return app

    @staticmethod
    def _define_routes(schema, app, service):
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

        @app.get(f"/{slug}/schema")
        @openapi.tag(name)
        @openapi.summary("Get JSON Schema")
        @openapi.description("Route to get the api JSON Schema.")
        @openapi.response(200, {"application/json": None}, "Success to get JSON Schema.")
        async def _get_schema(request):
            return response.json(schema)

        if "list" in enabled_handlers:
            @app.get(f"/{slug}")
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
                page = PYRSanicAppBuilder._get_query_string_arg(request.args, "page")
                size = PYRSanicAppBuilder._get_query_string_arg(request.args, "size")

                result = await service.list(slug, page, size)

                return response.json(result)

        if "create" in enabled_handlers:
            @app.post(f"/{slug}")
            @app.post(f"/{slug}/<id>")
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
                resource_id = await service.create(slug, request.json, id)
                return response.json({"id": resource_id}, status=201)

        if "get" in enabled_handlers:
            @app.get(f"/{slug}/<id>")
            @openapi.tag(name)
            @openapi.summary("Get a entity by id")
            @openapi.description("Route to get a entity by id.")
            @openapi.response(200, {"application/json": None}, "Success to get the entity.")
            @openapi.response(404, {"application/json": None}, "Entity not found.")
            @openapi.response(500, {"application/json": None}, "Internal server error.")
            @openapi.parameter("id", location="path")
            async def _get(request, id):
                result = await service.get(slug, id)
                return response.json(result)

        if "replace" in enabled_handlers:
            @app.put(f"/{slug}/<id>")
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
                await service.replace(slug, request.json, id)
                return response.json({})

        if "partial_update" in enabled_handlers:
            @app.patch(f"/{slug}/<id>")
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
                await service.partial_update(slug, request.json, id)
                return response.json({})

        if "delete" in enabled_handlers:
            @app.delete(f"/{slug}/<id>")
            @openapi.tag(name)
            @openapi.summary("Delete a entity by id")
            @openapi.description("Route to delete a entity.")
            @openapi.response(200, {"application/json": None}, "Success to delete the entity.")
            @openapi.response(500, {"application/json": None}, "Internal server error.")
            @openapi.parameter("id", location="path")
            async def _delete(request, id):
                await service.delete(slug, id)
                return response.json({})

    @staticmethod
    def _get_query_string_arg(query_string, arg_name):
        arg = query_string.get(arg_name, [])

        if type(arg) is not list:
            return arg

        if len(arg) == 1:
            return arg[0]

        if len(arg) > 1:
            return arg


class CustomErrorHandler(ErrorHandler):

    def default(self, request, exception):

        if isinstance(exception, PYRInputNotValidError):
            return response.json({"message": exception.message}, status=400)

        if isinstance(exception, PYRNotFoundError):
            return response.json({"message": exception.message}, status=404)

        if not isinstance(exception, SanicException):
            return response.json({"message": "Internal Server Error"}, status=500)

        return super().default(request, exception)
