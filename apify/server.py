import yaml

from sanic import Sanic
from sanic import response

from apify.repos.mongo import MongoRepo
from apify.repos import DatabaseError
from apify import settings


def read_api_params_from_yaml():
    api = None

    with open(r'./api.yaml') as file:
        api = yaml.load(file, Loader=yaml.FullLoader)

    return api


api = read_api_params_from_yaml()
app = Sanic(api['slug'])
repo = MongoRepo()


def get_query_string_arg(query_string, arg_name):
    args = query_string.get('page', [])
    
    if len(args) == 1:
        return args[0]

    if len(args) > 1:
        return args
    
    return None


def validate(resource):
    return None


async def _post(request, id=None):
    try:
        errors = validate(request.json)

        if errors:
            return response.json({'errors': errors}, status=400)

        resource_id = await repo.create(request.json, id)
        
        return response.json({'id': resource_id}, status=201)
    except DatabaseError as db_error:
        return response.json({'message': db_error.user_message}, status=500)
    except Exception as error:
        return response.json({}, status=500)


@app.route(f'/{api["slug"]}/schema', methods=['GET'])
async def get(request):
    return response.json(api['schema'])


@app.route(f'/{api["slug"]}', methods=['GET'])
async def get(request):
    try:
        page = get_query_string_arg(request.args, 'page')
        size = get_query_string_arg(request.args, 'size')

        result = await repo.list(page, size)

        return response.json(result)
    except DatabaseError as db_error:
        return response.json({'message': db_error.user_message}, status=500)
    except Exception as error:
        return response.json({}, status=500)


@app.route(f'/{api["slug"]}/<id>', methods=['GET'])
async def list(request, id):
    try:
        result = await repo.get(id)
        
        if result:
            return response.json(result)

        return response.json({}, status=404)
    except DatabaseError as db_error:
        return response.json({'message': db_error.user_message}, status=500)
    except Exception as error:
        return response.json({}, status=500)


@app.route(f'/{api["slug"]}', methods=['POST'])
async def post(request):
    return await _post(request)

@app.route(f'/{api["slug"]}/<id>', methods=['POST'])
async def post_with_id(request, id):
    return await _post(request, id)


@app.route(f'/{api["slug"]}/<id>', methods=['PUT'])
async def put(request, id):
    try:
        errors = validate(request.json)

        if errors:
            return response.json({'errors': errors}, status=400)

        resource_id = await repo.replace(id, request.json)

        if resource_id:
            return response.json({'id': resource_id})

        return response.json({}, status=404)
    except DatabaseError as db_error:
        return response.json({'message': db_error.user_message}, status=500)
    except Exception as error:
        return response.json({}, status=500)


@app.route(f'/{api["slug"]}/<id>', methods=['PATCH'])
async def patch(request, id):
    try:
        errors = validate(request.json)

        if errors:
            return response.json({'errors': errors}, status=400)

        resource_id = await repo.update(id, request.json)

        if resource_id:
            return response.json({'id': resource_id})

        return response.json({}, status=404)
    except DatabaseError as db_error:
        return response.json({'message': db_error.user_message}, status=500)
    except Exception as error:
        return response.json({}, status=500)


@app.route(f'/{api["slug"]}/<id>', methods=['DELETE'])
async def delete(request, id):
    try:
        await repo.delete(id)
        return response.json()
    except DatabaseError as db_error:
        return response.json({'message': db_error.user_message}, status=500)
    except Exception as error:
        return response.json({}, status=500)

if __name__ == '__main__':
    app.run(
        host='0.0.0.0', 
        port=8000, 
        debug=settings.DEBUG, 
        auto_reload=settings.AUTO_RELOAD
    )
