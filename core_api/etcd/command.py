import subprocess

from fastapi import HTTPException


def run_command(command: list[str]):
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        # Handle etcd connection error
        if "connection" in e.stderr.lower():
            raise HTTPException(status_code=503, detail=f"ETCD cluster connection error: {e.stderr.strip()}")
        else:
            raise HTTPException(status_code=500, detail=f"ETCD error: {e.stderr.strip()}")
    return result.stdout
