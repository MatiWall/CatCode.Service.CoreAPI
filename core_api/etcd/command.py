import subprocess

from fastapi import HTTPException

from settings import config

DEFAULT_PARAMS = [ 'etcdctl', f'--endpoints={config.etcd_host}']

ENV_VAR = {'ETCDCTL_API': '3'}

def run_command(command: list[str]):

    command = [*DEFAULT_PARAMS, *command]
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=ENV_VAR)
    except subprocess.CalledProcessError as e:
        # Handle etcd connection error
        if "connection" in e.stderr.lower():
            raise HTTPException(status_code=503, detail=f"ETCD cluster connection error: {e.stderr.strip()}")
        else:
            raise HTTPException(status_code=500, detail=f"ETCD error: {e.stderr.strip()}")
    return result.stdout
