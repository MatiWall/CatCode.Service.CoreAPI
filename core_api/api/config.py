import copy

import yaml
import settings
from fastapi import APIRouter


router = APIRouter(prefix='/config')
PATH = settings.BASE_DIR / 'configs/catcode-config.yaml'


def merge_dicts(dict1, dict2):
    result = copy.deepcopy(dict1)
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)  # Recursive call for nested dicts
        else:
            result[key] = value
    return result

def read_yaml_file(file_path):
    with open(file_path, 'r') as yaml_file:
        data = yaml.load(yaml_file, Loader=yaml.FullLoader)
    return data
@router.get('/')
def return_config():
    config = read_yaml_file(PATH)
    return config

@router.get('/{key}')
def return_config(key):
    config = read_yaml_file(PATH)
    return config[key]


