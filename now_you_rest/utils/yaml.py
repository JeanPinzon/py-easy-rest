import yaml


def read_api_params_from_yaml(api_config_path):
    api = None

    with open(api_config_path) as file:
        api = yaml.load(file, Loader=yaml.FullLoader)

    return api
