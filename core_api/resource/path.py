

def resource_path_builder(resource: dict):
    apigroup, apiversion = resource['apiVersion'].split('/')
    name = resource['metadata']['name']