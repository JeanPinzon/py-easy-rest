import yaml

from sanic import Sanic
from sanic import response

from apify.repos.mongo import MongoRepo
from apify.repos import DatabaseError


def read_api_params_from_yaml():
    api = None

    with open(r"./api.yaml") as file:
        api = yaml.load(file, Loader=yaml.FullLoader)

    return api


api = read_api_params_from_yaml()
app = Sanic(api["slug"])
repo = MongoRepo()


def get_query_string_arg(query_string, arg_name):
    args = query_string.get("page", [])
    
    if len(args) == 1:
        return args[0]

    if len(args) > 1:
        return args
    
    return None


def validate(resource):
    return None


async def post(request, id=None):      
    errors = validate(request.json)

    if errors:
        return response.json({"errors": errors}, status=400)

    resource_id = await repo.create(request.json, id)
    
    return response.json({"id": resource_id}, status=201)


async def list(request, id):
    result = await repo.get(id)
    
    if result:
        return response.json(result)

    return response.json({}, status=404)


async def get(request):
    page = get_query_string_arg(request.args, "page")
    size = get_query_string_arg(request.args, "size")

    result = await repo.list(page, size)

    return response.json(result)


async def put(request, id):
    errors = validate(request.json)

    if errors:
        return response.json({"errors": errors}, status=400)

    resource_id = await repo.replace(id, request.json)

    if resource_id:
        return response.json({"id": resource_id})

    return response.json({}, status=404)


async def patch(request, id):
    errors = validate(request.json)

    if errors:
        return response.json({"errors": errors}, status=400)

    resource_id = await repo.update(id, request.json)

    if resource_id:
        return response.json({"id": resource_id})

    return response.json({}, status=404)


async def delete(request, id):
    await repo.delete(id)
    return response.json()


handlers_without_id = {
    "GET": get,
    "POST": post,
}

handlers_with_id = {
    "GET": list,
    "POST": post,
    "PATCH": patch,
    "PUT": put,
    "DELETE": delete,
}


async def handle_request(handlers, request, *args):
    try:
        return await handlers[request.method](request, args)
    except DatabaseError as db_error:
        return response.json({"message": db_error.user_message}, status=500)
    except Exception as error:
        return response.json({}, status=500)


@app.route(f"/{api['slug']}", methods=["GET", "POST"])
async def handler_without_id(request):
    return await handle_request(handlers_without_id, request)


@app.route(f"/{api['slug']}/<id>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def handler_with_id(request, id):
    return await handle_request(handlers_with_id, request, id)


@app.route(f"/{api['slug']}/schema", methods=["GET"])
async def get_schema(request):
    print(request.method)
    return response.json(api["schema"])