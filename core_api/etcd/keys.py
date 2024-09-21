from typing import Optional

from fastapi import HTTPException

from core_api.etcd.cache import ResourceDefinitionCache, resource_definition_cache


class KeyBuilder:
    def __init__(
            self,
            resource_definition_cache: ResourceDefinitionCache,
            prefix: str = '/registry'
    ):
        self.resource_definition_cache = resource_definition_cache
        self.prefix = prefix

    def from_resource(self, resource: dict) -> str:
        group, version = resource['apiVersion'].split('/')

        if group == 'api.catcode.io':
            # Construct the key for a resource definition
            return self.prefix + f'/api.catcode.io/resourcedefinition/{resource["spec"]["group"]}/{resource["spec"]["names"]["singular"]}'
        else:
            # Get the singular name from the cache
            singular_name = self.resource_definition_cache.get_singular_name(resource)
            if singular_name is None:
                raise HTTPException(status_code=404,
                                    detail=f'No resource definition matches {resource["apiVersion"]} and {resource["kind"]}')
            group, _ = resource['apiVersion'].split('/')
            # Construct the key for a standard resource
            return self.prefix + f"/{group}/{singular_name}/{resource['metadata']['name']}"

    def from_request(self, type: str, name: Optional[str] = None):
        """
            Should be able to handle resource on the following formats

            components: plural name
            component: singular name
            components.catcode.io: <plural>.<api-group>
            component.catcode.io: <singluar>.<api-group>
            components.catcode.io/v1alpha1: <plural>.<api-group>/<version>
            component.catcode.io/v1alpha1: <singular>.<api-group>/<version>

            note following is also valid
            templates.templating.catcode.io/v1alpha1: <singular>.<api-group>/<version>
            as the fire . seperated the name from the group.


            If api group is not added it should "try" to look it up it self.
            If version is not added it should use the newest.s:

        """
        if 'resourcedefinition' == type:
            names = self.resource_definition_cache._singular_name[name]
            path = f'/api.catcode.io/resourcedefinition/{names["group"]}/{names["singular"]}'
        else:
            names = self.resource_definition_cache._singular_name[type]
            path = f"/{names['group']}/{type}/{name}"

        return self.prefix + path

key_builder = KeyBuilder(resource_definition_cache)