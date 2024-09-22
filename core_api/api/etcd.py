import json
from typing import Optional

from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from core_api.etcd.cache import resource_definition_cache
from core_api.etcd.command import run_command
from core_api.etcd.keys import key_builder
from core_api.etcd.validate import resource_validator
from settings import config

router = APIRouter(prefix='/resource/v1')

@router.post("/")
def post_resource(resource: dict):

    path = key_builder.from_resource(resource)
    if 'api.catcode.io' in resource['apiVersion']:
        resource_definition_cache.add_resource(resource)
    else:
        resource = resource_validator(resource)

    command = ['etcdctl', f'--endpoints={config.etcd_host}', 'put', path, json.dumps(resource)]
    run_command(command)
    return {"key": path, "value": resource}


@router.get('/{type}/{name}')
def get_resources(type: str, name: str = ''):
    """
    Should be able to handle resource on the following formats

    components: plural name
    component: singular name
    components.catcode.io: <plural>.<api-group>
    component.catcode.io: <singluar>.<api-group>
    components.catcode.io/v1alpha1: <plural>.<api-group>/<version>
    component.catcode.io/v1alpha1: <singular>.<api-group>/<version>

    note following is also valid
    templates.templating.catcode.io/v1alpha1: <singular>.<api-group>/<version>
    as the fire . seperated the name from the group.


    If api group is not added it should "try" to look it up it self.
    If version is not added it should use the newest.



    """

    path = key_builder.from_request(type, name)

    command = ['etcdctl', f'--endpoints={config.etcd_host}', 'get', path, '--print-value-only']

    try:
        output = run_command(command)

        if output:
            return {"key": path, "value": json.loads(output.strip()), 'exists': True}
        else:
            return {"key": path, "value": '', 'exists': False}
    except HTTPException as e:
        raise e



@router.delete('/{type}/{name}')
def delete_resources(type: str, name: str = ''):

    path = key_builder.from_request(type, name)

    command = ['etcdctl', f'--endpoints={config.etcd_host}', 'del', path]
    try:
        output = run_command(command)
        if "1" in output.lower():
            return {"key": path, "status": "deleted"}
        else:
            raise HTTPException(status_code=404, detail="Resource not found")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting resource: {str(e)}")

@router.put('/')
def put_resource(resource: dict):
    path = key_builder.from_resource(resource)

    command = ['etcdctl', f'--endpoints={config.etcd_host}', 'put', path, json.dumps(resource)]
    try:
        output = run_command(command)
        return {"key": path, "status": "created_or_updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating resource: {str(e)}")
