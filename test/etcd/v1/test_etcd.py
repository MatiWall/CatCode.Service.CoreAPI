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
    subprocess.run(["docker", "compose", "-f", BASE_DIR / 'docker-compose.yaml', "up", "-d"], check=True)
    os.environ['ETCDCTL_API'] = '3'
    # Wait for services to initialize (optional, adjust as needed)
    time.sleep(2)

    yield  # Run the tests

    # Stop Docker Compose
    subprocess.run(["docker", "compose", "-f", BASE_DIR / 'docker-compose.yaml', "down"], check=True)


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
                    "schemaVersion": "openAPISchemaV3",
                    "schema": {
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
                }
            ]
        }
    }
    return obj


@pytest.fixture
def mock_resources():
    obj = {
        'apiVersion': 'catcode.io/v1alpha1',
        'kind': 'System',
        'metadata': {'name': 'test'},
        'spec': {'owner': 'test'}
    }
    return obj

@pytest.fixture
def mock_resources2():
    obj = {
        'apiVersion': 'catcode.io/v1alpha1',
        'kind': 'System',
        'metadata': {'name': 'test2'},
        'spec': {'owner': 'test', 'nested': {'inner': 'yes'}}
    }
    return obj


@pytest.mark.order(1)
def test_custom_resource_insert(mock_resource_definition):
    # Insert the resource
    resp = client.post('/resource/v1', json=mock_resource_definition)

    # Check if the POST request was successful
    assert resp.status_code == 200, f"Failed to insert resource: {resp.content}"

    # Verify the inserted resource matches the mock resource definition
    retrieved = resp.json()['resource']
    assert retrieved == mock_resource_definition, "Inserted resource does not match"

    # Retrieve the inserted resource
    resp = client.get('/resource/v1/resourcedefinition/system')

    # Check if the GET request was successful
    assert resp.status_code == 200, f"Failed to retrieve resource: {resp.content}"

    # Verify the retrieved resource matches the mock resource definition
    retrieved = resp.json()['resource']
    assert retrieved == mock_resource_definition, "Retrieved resource does not match"


@pytest.mark.order(2)
def test_resource_insert(mock_resources):
    resp = client.post('/resource/v1', json=mock_resources)

    assert resp.status_code == 200, f"Failed to post resource {mock_resources} with error {resp.content}"

    resp = client.get('/resource/v1/system/test')

    assert resp.status_code == 200, f"Failed to get resource {mock_resources} with error {resp.content}"
    retrieved = resp.json()['resource']
    assert retrieved == mock_resources


@pytest.mark.order(3)
def test_resource_put(mock_resources):
    mock_resources['spec'] = {'updated': 'resource', 'owner': 'test'}

    resp = client.put('/resource/v1', json=mock_resources)

    assert resp.status_code == 200, f"Failed to put resource {mock_resources} with error {resp.content}"

    resp = client.get('/resource/v1/system/test')

    assert resp.status_code == 200, f"Failed to get resource {mock_resources} with error {resp.content}"
    retrieved = resp.json()['resource']
    assert retrieved == mock_resources

@pytest.mark.order(4)
def test_resource_patch(mock_resources2):
    resp = client.post('/resource/v1', json=mock_resources2)

    path = '/resource/v1/system/test2'

    patch_data = {"spec": {"nested": {"inner": "updated inner"}}}

    resp = client.patch(path, json=patch_data)

    assert resp.status_code == 200, f"Failed to patch resource {path} with error {resp.content}"

    resp = client.get(path)
    assert resp.status_code == 200, f"Failed to retrieve resource {path} after patch with error {resp.content}"
    assert resp.json()["resource"]["spec"]["nested"]["inner"] == "updated inner", "Resource patch did not update correctly"

@pytest.mark.order(5)
def test_get_multiple():

    path = '/resource/v1/systems'

    resp = client.get(path)

    assert resp.status_code == 200, f"Failed to fetch resources {path} with error {resp.content}"

    resources = resp.json()['resources']
    assert len(resources) > 1, f"Failed to retrieve resource {path} after patch with error {resp.content}"

@pytest.mark.order(6)
def test_resource_delete(mock_resources):
    path = '/resource/v1/system/test'
    resp = client.delete(path)

    assert resp.status_code == 200, f"Failed to delete resource {path} with error {resp.content}"

    # Step 4: Verify the resource was deleted
    resp = client.get(path)
    assert resp.status_code == 404, f"Resource {path} was not deleted"



