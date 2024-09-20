

class ResourceDefinitionCache:
    def __init__(self):
        self.singular_name = {}
        self.plural_name = {}

    def add_resource(self, resource):
        singular = self._get_singular_name(resource)
        plural = self._get_plural_name(resource)

        resource_data = {
            'group': resource['spec']['group'],
            'kind': resource['spec']['names']['kind'],
            'plural': resource['spec']['names']['plural'],
            'singular': resource['spec']['names']['singular']
        }

        self.singular_name[singular] = resource_data
        self.plural_name[plural] = resource_data

    def remove(self, resource):

        del self.singular_name[self._get_singular_name(resource)]
        del self.plural_name[self._get_plural_name(resource)]

    @staticmethod
    def _get_singular_name(resource):
        return resource['spec']['names']['singular']

    @staticmethod
    def _get_plural_name(resource):
        return resource['spec']['names']['plural']


resource_definition_cache = ResourceDefinitionCache()