import subprocess
import os
import pytest
import time
import json
from fastapi.testclient import TestClient
from fastapi.exceptions import HTTPException
from settings import BASE_DIR

from main import app

client = TestClient(app)

def dict_formatter(obj1):
    return json.dumps(obj1, sort_keys=True)

@pytest.fixture(scope="session", autouse=True)
def docker_compose():
    """Start and stop Docker Compose before and after tests."""
    # Start Docker Compose
    subprocess.run(["docker", "compose", "-f", BASE_DIR/'docker-compose.yaml', "up", "-d"], check=True)
    os.environ['ETCDCTL_API'] = '3'
    # Wait for services to initialize (optional, adjust as needed)
    time.sleep(2)

    yield  # Run the tests

    # Stop Docker Compose
    subprocess.run(["docker", "compose", "-f",  BASE_DIR/'docker-compose.yaml', "down"], check=True)

@pytest.fixture
def mock_resource_definition():

    obj = {
    "apiVersion": "api.catcode.io/v1alpha1",
    "kind": "ResourceDefinition",
    "metadata": {
        "name": "SystemResourceDefinition"
    },
    "spec": {
        "group": "catcode.io",
        "names": {
            "plural": "systems",
            "singular": "system",
            "kind": "System"
        },
        "versions": [
            {
                "name": "v1alpha1",
                "schema": {
                    "openAPISchemaV3": {
                        "type": "object",
                        "properties": {
                            "spec": {
                                "type": "object",
                                "properties": {
                                    "owner": {
                                        "type": "string"
                                    }
                                },
                                "required": [
                                    "owner"
                                ]
                            }
                        },
                        "required": [
                            "spec"
                        ]
                    }
                }
            }
        ]
    }
}
    return obj


@pytest.fixture
def mock_resources():

    obj =  {
        'apiVersion': 'catcode.io/v1alpha1',
        'kind': 'System',
        'metadata': {'name': 'test'},
        'spec': {'test': 'test'}
    }
    return obj

@pytest.mark.order(1)
def test_custom_resource_insert(mock_resource_definition):
    # Insert the resource
    resp = client.post('/resource', json=mock_resource_definition)

    # Check if the POST request was successful
    assert resp.status_code == 200, f"Failed to insert resource: {resp.content}"

    # Verify the inserted resource matches the mock resource definition
    retrieved = resp.json()['value']
    assert retrieved == mock_resource_definition, "Inserted resource does not match"

    # Retrieve the inserted resource
    resp = client.get('/resource/resourcedefinition/system')

    # Check if the GET request was successful
    assert resp.status_code == 200, f"Failed to retrieve resource: {resp.content}"

    # Verify the retrieved resource matches the mock resource definition
    retrieved = resp.json()['value']
    assert dict_formatter(retrieved) == dict_formatter(mock_resource_definition), "Retrieved resource does not match"

@pytest.mark.order(2)
def test_resource_insert(mock_resources):
    resp = client.post('/resource', json=mock_resources)

    assert resp.status_code == 200, f"Failed to post resource {mock_resources} with error {resp.content}"

    resp = client.get('/resource/system/test')

    assert resp.status_code == 200, f"Failed to get resource {mock_resources} with error {resp.content}"
    retrieved = resp.json()['value']
    assert retrieved == mock_resources

@pytest.mark.order(3)
def test_resource_delete():
    path = '/resource/system/test'
    resp = client.delete(path)

    assert resp.status_code == 200, f"Failed to delete resource {path} with error {resp.content}"