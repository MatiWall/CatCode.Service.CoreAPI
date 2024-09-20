import pytest

from core_api.etcd.retrieve import fetch_resource_definition


def test_fetch_resource():
    objects = fetch_resource_definition('user')