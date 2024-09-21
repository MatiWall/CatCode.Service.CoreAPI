from core_api.etcd.cache import ResourceDefinitionCache


class ResourceValidator:
    def __init__(
            self,
            resource_definition_cache: ResourceDefinitionCache,
    ):
        self.resource_definition_cache = resource_definition_cache

    def validate(self):
        pass