import yaml

from sanic import Sanic
from sanic import response

from apify.repos import DatabaseError


class App():
    
    def __init__(self, repo, api_config_path):
        self._repo = repo
        self._api_config_path = api_config_path
        self._api = App._read_api_params_from_yaml(api_config_path)

        self._handlers_without_id = {
            "GET": self._get,
            "POST": self._post,
        }

        self._handlers_with_id = {
            "GET": self._list,
            "POST": self._post,
            "PATCH": self._patch,
            "PUT": self._put,
            "DELETE": self._delete,
        }

        self.app = Sanic(self._api["slug"])

        self.app.add_route(
            self.handle_without_id, 
            f"/{self._api['slug']}", 
            methods=["GET", "POST"]
        )
        self.app.add_route(
            self.handle_with_id, 
            f"/{self._api['slug']}/<id>", 
            methods=["GET", "POST", "PUT", "PATCH", "DELETE"]
        )
        self.app.add_route(
            self.get_schema, 
            f"/{self._api['slug']}/schema", 
            methods=["GET"]
        )

    @staticmethod
    def _read_api_params_from_yaml(api_config_path):
        api = None

        with open(api_config_path) as file:
            api = yaml.load(file, Loader=yaml.FullLoader)

        return api


    @staticmethod
    def _get_query_string_arg(query_string, arg_name):
        args = query_string.get("page", [])
        
        if len(args) == 1:
            return args[0]

        if len(args) > 1:
            return args
        
        return None


    @staticmethod
    def _validate(resource):
        return None


    async def _post(self, request, id=None):      
        errors = App._validate(request.json)

        if errors:
            return response.json({"errors": errors}, status=400)

        resource_id = await self._repo.create(request.json, id)

        return response.json({"id": resource_id}, status=201)


    async def _list(self, request, id):
        result = await self._repo.get(id)
        
        if result:
            return response.json(result)

        return response.json({}, status=404)


    async def _get(self, request):
        page = App._get_query_string_arg(request.args, "page")
        size = App._get_query_string_arg(request.args, "size")

        result = await self._repo.list(page, size)

        return response.json(result)


    async def _put(self, request, id):
        errors = App._validate(request.json)

        if errors:
            return response.json({"errors": errors}, status=400)

        resource_id = await self._repo.replace(id, request.json)

        if resource_id:
            return response.json({"id": resource_id})

        return response.json({}, status=404)


    async def _patch(self, request, id):
        errors = App._validate(request.json)

        if errors:
            return response.json({"errors": errors}, status=400)

        resource_id = await self._repo.update(id, request.json)

        if resource_id:
            return response.json({"id": resource_id})

        return response.json({}, status=404)


    async def _delete(self, request, id):
        await self._repo.delete(id)
        return response.json()


    async def _handle_request(self, handlers, request, *args):
        try:
            return await handlers[request.method](request, args)
        except DatabaseError as db_error:
            return response.json({"message": db_error.user_message}, status=500)
        except Exception as error:
            return response.json({}, status=500)


    async def handle_without_id(self, request):
        return await self._handle_request(self._handlers_without_id, request)


    async def handle_with_id(self, request, id):
        return await self._handle_request(self._handlers_with_id, request, id)


    async def get_schema(self, request):
        return response.json(self._api["schema"])