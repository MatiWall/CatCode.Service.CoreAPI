

def resource_validation(resource: dict):
    if resource['kind'] == 'ResourceDefinition':
        return resource

    # resource_definition = 'api.catcode.io/'
    # todo: implement such that it fetched the resource definition and validated the definition aginst it.
    # might have to make a mapping between kind and singular and plural names
    return resource
