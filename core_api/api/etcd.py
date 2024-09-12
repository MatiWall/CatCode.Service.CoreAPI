import subprocess

from fastapi import APIRouter, Query
from fastapi.exceptions import HTTPException
from settings import config

router = APIRouter(prefix='/resource')

def run_etcd_command(command: list[str]):
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f'etcd error: {e.stderr.strip()}')
    return result.stdout

@router.get('/{path:path}')
def get_resource(path: str, prefix: bool = Query(default=False)):
    if prefix:
        command = ['etcdctl', f'--endpoints={config.etcd_host}', 'get', path, '--prefix']
    else:
        command = ['etcdctl', f'--endpoints={config.etcd_host}', 'get', path, '--print-value-only']
    output = run_etcd_command(command)
    if output:
        if prefix:
            keys = output.strip().split('\n')
            return {"prefix": path, "keys": keys}
        return {"key": path, "value": output.strip()}
    else:
        raise HTTPException(status_code=404, detail="Resource not found")

@router.post("/{path:path}")
def post_resource(path: str, value: str):
    command = ['etcdctl', f'--endpoints={config.etcd_host}', 'put', path, value]
    run_etcd_command(command)
    return {"key": path, "value": value}


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