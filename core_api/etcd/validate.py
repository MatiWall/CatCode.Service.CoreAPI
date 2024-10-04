import yaml
from fastapi import HTTPException
import jsonschema

from core_api.etcd.cache import ResourceDefinitionCache, resource_definition_cache
from settings import BASE_DIR


class ResourceValidator:
    def __init__(
            self,
            resource_definition_cache: ResourceDefinitionCache,
    ):
        self.resource_definition_cache = resource_definition_cache

        base_schemas = {}
        for name, schema in [('base-schema', 'schemas/base.yaml'),
                             ('base-resource-definition-schema', 'schemas/base-resource-definition.yaml')]:
            with (BASE_DIR / schema).open('r') as f:
                file = yaml.safe_load(f)
                base_schemas[name] = file
        self.base_schemas = base_schemas

    def __call__(self, resource: dict):
        return self.validate(resource)

    def validate(self, resource: dict):
        resource_definition = self.resource_definition_cache.get_resource_definition(resource)

        _, version = resource['apiVersion'].split('/')

        schema_spec = [s for s in resource_definition['spec']['versions'] if s['name'] == version]

        if len(schema_spec) == 0:
            raise HTTPException(status_code=400, detail=f'No resource schema found for resource: {resource}')
        elif len(schema_spec) > 1:
            raise HTTPException(status_code=400, detail=f'Multiple schemas found for resource: {resource}')

        schema_spec = schema_spec[0]

        # Validate the schema version
        if 'schemaVersion' not in schema_spec or schema_spec['schemaVersion'] != 'openAPISchemaV3':
            raise HTTPException(status_code=400, detail=f'Invalid schema version: {schema_spec.get("schemaVersion")}')

        if schema_spec['schemaVersion'] != 'openAPISchemaV3':
            raise HTTPException(status_code=400, detail=f'Invalid schema {schema_spec["schemaVersion"]}')

        schema = schema_spec['schema']
        # TODO: Implemnt base validation also.
        jsonschema.validate({'spec': resource['spec']}, schema)

        return resource

    def base_validation(self, resource: dict):
        try:
            jsonschema.validate(resource, self.base_schemas['base-schema'])
        except jsonschema.ValidationError as e:
            raise HTTPException(status_code=400, detail=f"Validation Error: {e.message}")
        return resource

    def base_resource_validation(self, resource: dict):
        jsonschema.validate(resource, self.base_schemas['base-resource-definition-schema'])
        return resource

resource_validator = ResourceValidator(resource_definition_cache)

