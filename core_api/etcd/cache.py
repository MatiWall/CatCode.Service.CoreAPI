

class ResourceDefinitionCache:
    def __init__(self):
        self._singular_name = {}
        self._plural_name = {}

    def add_resource(self, resource):
        singular = self._get_singular_name(resource)
        plural = self._get_plural_name(resource)

        resource_data = {
            'group': resource['spec']['group'],
            'kind': resource['spec']['names']['kind'],
            'plural': resource['spec']['names']['plural'],
            'singular': resource['spec']['names']['singular']
        }

        self._singular_name[singular] = resource_data
        self._plural_name[plural] = resource_data

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


resource_definition_cache = ResourceDefinitionCache()