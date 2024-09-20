from typing import Optional
import re

from core_api.etcd.retrieve import fetch_resource_definition


def resource_path_creator(resource: dict):
    if resource['kind'] == 'BaseSchema':
        return f'resource/registry/api.catcode.io/baseschema'
    elif resource['kind'] == 'ResourceDefinition':
        apigroup = resource['apiVersion'].split('/')[0]
        resource_group = resource['spec']['group']
        singular = resource['spec']['names']['singular']

        return f'resource/registry/{apigroup}/resourcedefinition/{resource_group}/{singular}'
    else:
        raise ValueError('To be implemented. Resource key')
        # command = ['etcdctl', f'--endpoints={config.etcd_host}', 'get', path, '--print-value-only']
        # output = run_command(command)
        # return f'resource/registry/{apigroup}/resourcedefinition/{resource_group}/{singular}'

def resource_path_builder(

        resource: str
):
    if bool(re.match("^[^./]+$", resource)):
        resource_definition = fetch_resource_definition(resource)