from sanic import Sanic, response
from jsonschema import Draft7Validator

from apify.repos import DatabaseError
from apify.utils.json import JSONEncoder
from apify.utils.yaml import read_api_params_from_yaml
from apify.utils.request import get_query_string_arg

json_dumps = JSONEncoder().encode


class App():

    def __init__(self, repo, api_config_path):
        self._repo = repo
        self._api_config_path = api_config_path
        self._api = read_api_params_from_yaml(api_config_path)
        self._schema = None

        self._handlers_without_id = {
            "GET": self._list,
            "POST": self._post,
        }

        self._handlers_with_id = {
            "GET": self._get,
            "POST": self._post,
            "PATCH": self._patch,
            "PUT": self._put,
            "DELETE": self._delete,
        }

        self.app = Sanic(self._api["slug"])
        self._define_routes()

    @property
    def api_schema(self):
        if self._schema is None:
            self._schema = self._api["schema"]
            self._schema["additionalProperties"] = False

        return self._schema

    def _validate(self, resource):
        validator = Draft7Validator(self.api_schema)

        errors = []

        for error in validator.iter_errors(resource):
            errors.append(error.message)

        if len(errors) > 0:
            return errors

        return None

    def _define_routes(self):
        self.app.add_route(
            self.handle_without_id,
            f"/{self._api['slug']}",
            methods=["GET", "POST"],
        )
        self.app.add_route(
            self.handle_with_id,
            f"/{self._api['slug']}/<id>",
            methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        )
        self.app.add_route(
            self.get_schema,
            f"/{self._api['slug']}/schema",
            methods=["GET"],
        )

    async def _post(self, request, id=None):
        errors = self._validate(request.json)

        if errors:
            return response.json({"errors": errors}, status=400, dumps=json_dumps)

        resource_id = await self._repo.create(request.json, id)

        return response.json({"id": resource_id}, status=201, dumps=json_dumps)

    async def _get(self, request, id):
        result = await self._repo.get(id)

        if result:
            return response.json(result, dumps=json_dumps)

        return response.json({}, status=404, dumps=json_dumps)

    async def _list(self, request):
        page = get_query_string_arg(request.args, "page")
        size = get_query_string_arg(request.args, "size")

        if page is not None:
            page = int(page)

        if size is not None:
            size = int(size)

        result = await self._repo.list(page, size)

        return response.json(result, dumps=json_dumps)

    async def _put(self, request, id):
        errors = self._validate(request.json)

        if errors:
            return response.json({"errors": errors}, status=400, dumps=json_dumps)

        await self._repo.replace(id, request.json)

        return response.json({}, dumps=json_dumps)

    async def _patch(self, request, id):
        errors = self._validate(request.json)

        if errors:
            return response.json({"errors": errors}, status=400, dumps=json_dumps)

        await self._repo.update(id, request.json)

        return response.json({}, dumps=json_dumps)

    async def _delete(self, request, id):
        await self._repo.delete(id)
        return response.json({}, dumps=json_dumps)

    async def handle_without_id(self, request):
        try:
            return await self._handlers_without_id[request.method](request)
        except DatabaseError as db_error:
            return response.json({"message": db_error.user_message}, status=500, dumps=json_dumps)
        except Exception:
            return response.json({}, status=500, dumps=json_dumps)

    async def handle_with_id(self, request, id):
        try:
            return await self._handlers_with_id[request.method](request, id)
        except DatabaseError as db_error:
            return response.json({"message": db_error.user_message}, status=500, dumps=json_dumps)
        except Exception:
            return response.json({}, status=500, dumps=json_dumps)

    async def get_schema(self, request):
        return response.json(self.api_schema, dumps=json_dumps)
