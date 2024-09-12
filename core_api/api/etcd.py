import subprocess
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from settings import config

router = APIRouter(prefix='/resource')

def run_etcd_command(command: list[str]):
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f'etcd error: {e.stderr.strip()}')
    return result

@router.get('/{key}')
def get_resource(key):
    command = ['etcdctl', f'--endpoints={config.etcd_host}', 'get', key]
    output = run_etcd_command(command)
    if output:
        return {"key": key, "value": output.strip()}
    else:
        raise HTTPException(status_code=404, detail="Resource not found")

@router.post("/{key}")
def post_resource(key: str, value: str):
    command = ['etcdctl', f'--endpoints={config.etcd_host}', 'put', key, value]
    run_etcd_command(command)
    return {"key": key, "value": value}

@router.get("/{prefix}")
def get_resources(prefix: str):
    command = ['etcdctl', f'--endpoints={config.etcd_host}', 'get', prefix, '--prefix']
    output = run_etcd_command(command)
    keys = output.strip().split('\n')
    return {"prefix": prefix, "keys": keys}