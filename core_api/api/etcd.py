import json

from fastapi import APIRouter, Query
from fastapi.exceptions import HTTPException

from core_api.etcd.command import run_command
from core_api.resource.validation import resource_validation
from settings import config

router = APIRouter(prefix='/resource')


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


@router.post("/{path:path}")
def post_resource(path: str, resource: dict):

    resource = resource_validation(resource)

    command = ['etcdctl', f'--endpoints={config.etcd_host}', 'put', path, json.dumps(resource)]
    run_command(command)
    return {"key": path, "value": resource}


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