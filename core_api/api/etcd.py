import json
from typing import Optional

import yaml
from fastapi import APIRouter, FastAPI, Depends, Request
from fastapi.exceptions import HTTPException

from core_api.etcd.cache import resource_definition_cache
from core_api.etcd.command import run_command
from core_api.etcd.keys import key_builder
from core_api.etcd.validate import resource_validator
from settings import config, BASE_DIR

router = APIRouter(prefix='/resource/v1')

@router.post("/")
def post_resource(resource: dict):

    resource_validator.base_validation(resource)

    path = key_builder.from_resource(resource)
    if 'api.catcode.io' in resource['apiVersion']:
        resource_validator.base_resource_validation(resource)
        resource_definition_cache.add_resource(resource)
    else:
        resource = resource_validator(resource)

    command = ['etcdctl', f'--endpoints={config.etcd_host}', 'put', path, json.dumps(resource)]
    run_command(command)
    return {"key": path, "resource": resource}


@router.get('/{type}')
def get_resources(type: str):
    """
    Should be able to handle resource on the following formats:

    components: plural name
    component: singular name
    components.catcode.io: <plural>.<api-group>
    component.catcode.io: <singular>.<api-group>
    components.catcode.io/v1alpha1: <plural>.<api-group>/<version>
    component.catcode.io/v1alpha1: <singular>.<api-group>/<version>

    note following is also valid:
    templates.templating.catcode.io/v1alpha1: <singular>.<api-group>/<version>
    as the first "." separates the name from the group.

    If the api group is not added, it should try to look it up itself.
    If the version is not added, it should use the newest.
    """
    # Check if the resource type exists and is plural
    if not resource_definition_cache.exists(type):
        raise HTTPException(status_code=404, detail=f"Resource {type} does not exist.")

    if not resource_definition_cache.is_plural(type):
        raise HTTPException(status_code=400, detail=f"Please use plural names when requesting multiple resources.")

    # Build the key prefix path for etcd
    path_prefix = key_builder.from_request(type)

    # Use etcdctl to get all resources with the matching prefix
    command = ['etcdctl', f'--endpoints={config.etcd_host}', 'get', path_prefix, '--prefix', '--print-value-only']

    try:
        output = run_command(command)

        # Check if the output contains any results
        if output:
            # Split the output by lines (assuming one resource per line)
            resources = output.strip().splitlines()

            # Parse each resource (assuming the values are JSON objects)
            resource_list = [json.loads(resource) for resource in resources]

            return {"key_prefix": path_prefix, "resources": resource_list, "count": len(resource_list)}
        else:
            raise HTTPException(status_code=404, detail=f"No resources found for {path_prefix}")

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving resources: {str(e)}")

@router.get('/{type}/{name}')
def get_resource(type: str, name: str = ''):
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
    if not resource_definition_cache.exists(type) and type != 'resourcedefinition':
        raise HTTPException(status_code=404, detail=f'Resource {type} does not exists.')

    if not resource_definition_cache.is_singular(type) and type != 'resourcedefinition':
        raise HTTPException(status_code=400, detail=f'Please use singular names when requesting specific resources')

    path = key_builder.from_request(type, name)


    command = ['etcdctl', f'--endpoints={config.etcd_host}', 'get', path, '--print-value-only']

    try:
        output = run_command(command)

        if output:
            return {"key": path, "resource": json.loads(output.strip()), 'exists': True}
        else:
            raise HTTPException(status_code=404, detail=f"Resource {path} does not exists")
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
    resource_validator.base_validation(resource)

    if 'api.catcode.io' in resource['apiVersion']:
        resource_validator.base_resource_validation(resource)
        resource_definition_cache.add_resource(resource)
    else:
        resource = resource_validator(resource)

    path = key_builder.from_resource(resource)

    command = ['etcdctl', f'--endpoints={config.etcd_host}', 'put', path, json.dumps(resource)]
    try:
        output = run_command(command)
        return {"key": path, "status": "created_or_updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating resource: {str(e)}")


@router.patch('/{type}/{name}')
def patch_resources(item: dict, type: str, name: str):
    # Build the path for the resource in etcd
    path = key_builder.from_request(type, name)

    # Command to get the current resource from etcd
    get_command = ['etcdctl', f'--endpoints={config.etcd_host}', 'get', path, '--print-value-only']

    try:
        # Retrieve the existing resource from etcd
        existing_resource = run_command(get_command)

        if not existing_resource:
            raise HTTPException(status_code=404, detail="Resource not found")

        # Convert the existing resource from JSON string to a Python dictionary
        existing_data = json.loads(existing_resource.strip())


        # Function to recursively update only existing fields
        def update_existing_fields(original: dict, updates: dict) -> dict:
            for key, value in updates.items():
                if key in original:
                    # If the value is a nested dictionary, recursively update it
                    if isinstance(value, dict) and isinstance(original[key], dict):
                        original[key] = update_existing_fields(original[key], value)
                    else:
                        # Only update if the key exists in the original data
                        original[key] = value
            return original

        # Update only the existing fields in the resource
        updated_data = update_existing_fields(existing_data, item)

        # Convert the updated resource back to JSON string
        updated_data = json.dumps(updated_data)

        # Command to put the updated resource back into etcd
        put_command = ['etcdctl', f'--endpoints={config.etcd_host}', 'put', path, updated_data]

        # Run the command to update the resource in etcd
        run_command(put_command)

        return {"key": path, "status": "updated", "resource": existing_data}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating resource: {str(e)}")