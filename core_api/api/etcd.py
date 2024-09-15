import subprocess
from csv import excel

from fastapi import APIRouter, Query
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

from settings import config

router = APIRouter(prefix='/resource')

def run_etcd_command(command: list[str]):
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        # Handle etcd connection error
        if "connection" in e.stderr.lower():
            raise HTTPException(status_code=503, detail=f"ETCD cluster connection error: {e.stderr.strip()}")
        else:
            raise HTTPException(status_code=500, detail=f"ETCD error: {e.stderr.strip()}")
    return result.stdout

@router.get('/{path:path}')
def get_resource(path: str, prefix: bool = Query(default=False)):
    if prefix:
        command = ['etcdctl', f'--endpoints={config.etcd_host}', 'get', path, '--prefix']
    else:
        command = ['etcdctl', f'--endpoints={config.etcd_host}', 'get', path, '--print-value-only']

    try:
        output = run_etcd_command(command)

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

class Resource(BaseModel):
    value: str

@router.post("/{path:path}")
def post_resource(path: str, resource: Resource):
    command = ['etcdctl', f'--endpoints={config.etcd_host}', 'put', path, resource.value]
    run_etcd_command(command)
    return {"key": path, "value": resource.value}


@router.delete('/{path:path}')
def delete_resource(path: str):
    command = ['etcdctl', f'--endpoints={config.etcd_host}', 'del', path]
    try:
        output = run_etcd_command(command)
        if "deleted" in output.lower():
            return {"key": path, "status": "deleted"}
        else:
            raise HTTPException(status_code=404, detail="Resource not found")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting resource: {str(e)}")