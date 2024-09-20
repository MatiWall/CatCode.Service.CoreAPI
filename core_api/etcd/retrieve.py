import json

from fastapi.exceptions import HTTPException

from core_api.etcd import run_command
from settings import config

def etcd_get(key):
    command = ['etcdctl', f'--endpoints={config.etcd_host}', 'get', key, '--print-value-only']
    value = run_command(command)
    return json.loads(value)

def etcd_get_keys_from_prefix(prefix) -> list[str]:

    keys_command = ['etcdctl', 'get', prefix, '--keys-only', '--prefix']
    keys = run_command(keys_command)
    return keys.splitlines()

def etcd_get_items_from_prefix(prefix: str) -> dict:
    lines_command = ['etcdctl', 'get', prefix, '--prefix']
    lines = run_command(lines_command)
    lines = lines.strip().splitlines()

    resources = {}
    for i in range(0, len(lines), 2):
        key = lines[i]
        value = lines[i + 1]

        resources[key] = value

    return resources

def fetch_resource_definitions(resource: str, group: str = None) -> dict[str, dict]:


    if group:
        keys = etcd_get_keys_from_prefix(resource)
        matching_keys = [key for key in keys if group in key]

        mapping = {}
        for key in matching_keys:
            mapping[key] = json.loads(etcd_get(key))
        return mapping

    return etcd_get_items_from_prefix(resource)

def fetch_resource_definition(resource, group: str = None, version: str = None ):


    resources = fetch_resource_definitions(resource, group)

    for key, resource_definition in resources.items():
        if (resource == resource_definition['spec']['names']['singular']) or (resource == resource_definition['spec']['names']['plural']):
            if version is None:
                return resource_definition['spec']['versions'][-1]
            elif version:
                schema = [s for s in resource_definition['spec']['versions'] if s['name'] == version]
                if len(schema) == 0:
                    raise HTTPException(status_code=404, detail=f'Resource {resource} with version {version} not found.')
                elif len(schema) == 1:
                    return schema[0]
                else:
                    raise HTTPException(status_code=404,
                                        detail=f'Multiple resources found for {resource} with version {version}.')


            return value

    return mapping