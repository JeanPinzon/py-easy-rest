from sanic import Sanic, response
from sanic_openapi import doc, swagger_blueprint
from jsonschema import Draft7Validator

from now_you_rest.repos import DatabaseError
from now_you_rest.utils.json import JSONEncoder
from now_you_rest.utils.yaml import read_api_params_from_yaml
from now_you_rest.utils.request import get_query_string_arg

json_dumps = JSONEncoder().encode


class App():

    def __init__(self, repo, api_config_path):
        self._repo = repo
        self._api_config_path = api_config_path
        self._api = read_api_params_from_yaml(api_config_path)
        self._schema = None

        self.app = Sanic(self._api["slug"])

        self.app.blueprint(swagger_blueprint)

        self.app.config["API_TITLE"] = self._api["name"]

        self.app.error_handler.add(DatabaseError, App._handle_database_error)

        self._define_routes()

    @property
    def api_schema(self):
        if self._schema is None:
            self._schema = self._api["schema"]
            self._schema["additionalProperties"] = False

        return self._schema

    @staticmethod
    async def _handle_database_error(request, exception):
        return response.json({"message": exception.user_message}, status=500, dumps=json_dumps)

    def _validate(self, resource):
        validator = Draft7Validator(self.api_schema)

        errors = []

        for error in validator.iter_errors(resource):
            errors.append(error.message)

        if len(errors) > 0:
            return errors

        return None

    def _define_routes(self):
        slug = self._api['slug']
        name = self._api['name']

        @self.app.get(f"/{slug}/schema")
        @doc.summary("Get JSON Schema")
        @doc.description("Route to get the api JSON Schema.")
        @doc.response(200, None, description="Success to get JSON Schema.")
        async def get_schema(request):
            return response.json(self.api_schema, dumps=json_dumps)

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

            result = await self._repo.list(page, size)

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
            errors = self._validate(request.json)

            if errors:
                return response.json({"errors": errors}, status=400, dumps=json_dumps)

            resource_id = await self._repo.create(request.json, id)

            return response.json({"id": resource_id}, status=201, dumps=json_dumps)

        @self.app.get(f"/{slug}/<id>")
        @doc.summary("Get a document by id")
        @doc.description(f"Route to get a {name} document by id.")
        @doc.response(200, None, description="Success to get the document.")
        @doc.response(404, None, description="Document not found.")
        @doc.response(500, None, description="Internal server error.")
        @doc.produces(doc.Dictionary())
        async def _get(request, id):
            result = await self._repo.get(id)

            if result:
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
            errors = self._validate(request.json)

            if errors:
                return response.json({"errors": errors}, status=400, dumps=json_dumps)

            await self._repo.replace(id, request.json)

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
            errors = self._validate(request.json)

            if errors:
                return response.json({"errors": errors}, status=400, dumps=json_dumps)

            await self._repo.update(id, request.json)

            return response.json({}, dumps=json_dumps)

        @self.app.delete(f"/{slug}/<id>")
        @doc.summary("Delere a document by id")
        @doc.description(f"Route to delete a document of {name}.")
        @doc.response(200, None, description="Success to delete the document.")
        @doc.response(500, None, description="Internal server error.")
        async def _delete(request, id):
            await self._repo.delete(id)
            return response.json({}, dumps=json_dumps)
