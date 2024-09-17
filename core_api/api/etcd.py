import json

from fastapi import APIRouter, Query
from fastapi.exceptions import HTTPException

from core_api.etcd.command import run_command
from core_api.resource.path import resource_path_builder
from core_api.resource.validation import resource_validation
from settings import config

router = APIRouter(prefix='/resource')


# def get_existing_resource(key):
#     command = ['etcdctl', 'get', key]
#     try:
#         result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
#         return result.stdout
#     except subprocess.CalledProcessError as e:
#         print(f"Error: {e.stderr}")
#         raise ValueError(f'Failed to retrieve resource for key')
#
#
# def update_resource(resource):
#     path = f'{config.core_api}'
#
#     resp = requests.get(path)
#     if resp.status_code == 200:
#         response = resp.json()
#         resource_exists = response.get('exists')
#         if resource_exists:
#             current_state = resp.json()['value']
#             current_state = json.loads(current_state)
#
#             if resource == current_state:
#                 logger.debug(f'State of object did not change, continuing.')
#                 return
#
#         logger.info(f'Resource changed: ')
#
#         if resp.status_code == 200:
#             logger.info(f'Successfully updated resource at {key}')
#         else:
#             logger.error(f'Failed to update resource at {key}')
#     else:
#         logger.error(f'Failed to read current state of resource {key}')
@router.post("/")
def post_resource(resource: dict):

    resource = resource_validation(resource)
    path = resource_path_builder(resource)
    command = ['etcdctl', f'--endpoints={config.etcd_host}', 'put', path, json.dumps(resource)]
    run_command(command)
    return {"key": path, "value": resource}


@router.get('/{path:path}')
def get_resource(path: str, prefix: bool = Query(default=False)):
    if prefix:
        command = ['etcdctl', f'--endpoints={config.etcd_host}', 'get', path, '--prefix']
    else:
        command = ['etcdctl', f'--endpoints={config.etcd_host}', 'get', path, '--print-value-only']

    try:
        output = run_command(command)

        if prefix:
            if output:
                keys = output.strip().split('\n')
                return {"prefix": path, "keys": keys, 'exists': True}
            else:
                return {"prefix": path, "keys": [], 'exists': False}

        if output:
            return {"key": path, "value": output.strip(), 'exists': True}
        else:
            return {"key": path, "value": '', 'exists': False}
    except HTTPException as e:
        raise e



@router.delete('/{path:path}')
def delete_resource(path: str):
    command = ['etcdctl', f'--endpoints={config.etcd_host}', 'del', path]
    try:
        output = run_command(command)
        if "deleted" in output.lower():
            return {"key": path, "status": "deleted"}
        else:
            raise HTTPException(status_code=404, detail="Resource not found")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting resource: {str(e)}")