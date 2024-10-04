

class ResourceDefinitionCache:
    def __init__(self):
        self._singular_name = {}
        self._plural_name = {}
        self._resources = {}

    def add_resource(self, resource):
        singular = self._get_singular_name(resource)
        plural = self._get_plural_name(resource)

        group = resource['spec']['group']
        kind = resource['spec']['names']['kind']


        resource_data = {
            'group': group,
            'kind': kind,
            'plural': plural,
            'singular': singular
        }

        self._singular_name[singular] = resource_data
        self._plural_name[plural] = resource_data
        self._resources[f'{group}/{singular}'] = resource

    def remove(self, resource):

        del self._singular_name[self._get_singular_name(resource)]
        del self._plural_name[self._get_plural_name(resource)]

    @staticmethod
    def _get_singular_name(resource):
        return resource['spec']['names']['singular']

    @staticmethod
    def _get_plural_name(resource):
        return resource['spec']['names']['plural']

    def get_singular_name(self, resource):

        for singular_name, values in self._singular_name.items():
            if resource['kind'] in values.values():
                return singular_name
        return None
    def get_resource_definition(self, resource: dict):
        group, _ = resource['apiVersion'].split('/')
        return self._resources[f'{group}/{self.get_singular_name(resource)}']

    def is_singular(self, name: str):
        if name in self._singular_name.keys():
            return True
        return False

    def is_plural(self, name: str):
        if name in self._plural_name.keys():
            return True
        return False

    def exists(self, name: str):
        return self.is_singular(name) or self.is_plural(name)

    def plural_names(self):
        return list(self._plural_name.keys())



resource_definition_cache = ResourceDefinitionCache()