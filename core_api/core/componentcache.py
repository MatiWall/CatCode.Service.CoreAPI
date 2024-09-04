import logging

from core_api.core.models import Application

logger = logging.getLogger(__name__)
from pathlib import Path
from typing import Optional, Union

from fastapi.exceptions import HTTPException

from core_api.core.reader.models import CatCodeRepoEntry
from settings import BASE_DIR


class ComponentCache:
    """
    A simple file system database class that stores data in YAML files.

    Parameters:
    - path (Path): The base directory where the YAML files are stored.

    Attributes:
    - path (Path): The base directory where the YAML files are stored.
    - cache (dict): A cache to store data retrieved from the file system.

    Methods:
    - get_all(): Retrieve all data from the file system.
    - get(id): Retrieve data for a specific ID, using the cache if available.
    - post(id, data): Insert or update data for a specific ID in the file system.
    - update(id, data): Update data for a specific ID in the file system.
    - delete(id): Delete data for a specific ID from the file system.
    """

    def __init__(self, path: Path):
        """
        Initialize the ComponentCache with the specified base directory.

        Parameters:
        - path (Path): The base directory where the YAML files are stored.
        """
        self.path = path
        self._cache = {}

    def add(self, component: Application):
        self._cache[(
            component.metadata.system,
            component.metadata.application,
            component.metadata.deployable_unit)
        ] = component
        return True

    def remove(self, component: Application):
        del self._cache[(
            component.metadata.system,
            component.metadata.application,
            component.metadata.deployable_unit
        )]
        return True
    def get_all(self):
        """
        Retrieve all data from the file system.

        Returns:
        dict: A dictionary containing all data from the file system.
        """
        return self._cache

    def get(self, id: Optional[tuple[str,str, str]] = None):
        """
        Retrieve data for a specific ID, using the cache if available.

        Parameters:
        - id (str): The ID for which to retrieve data.

        Returns:
        Any: The data associated with the specified ID, or None if not found.
        """
        if id is None:
            return list(self._cache.values())
        elif id in self._cache:
            return self._cache[id]

        raise HTTPException(status_code=404, detail=f'File with id "{id}" does not exist')



    def stats(self):

        output_list = [list(item) for item in zip(*list(self._cache.keys()))]
        return {
            'applications': len(list(set(output_list[1]))),
            'systems': len(list(set(output_list[0]))),
            'deployableUnits': len(list(output_list[2]))
        }

class TrackedPathsCache:
    def __init__(self):
        self._cache = {}

    def add(self, repo: CatCodeRepoEntry):
        if repo.name not in self._cache.keys():
            self._cache[repo.name] = repo.sha
            return 'New'
        elif repo.name in self._cache.keys() and repo.sha == self._cache[repo.name]:
            return 'NoChange'
        elif repo.name in self._cache.keys() and repo.sha != self._cache[repo.name]:
            return 'Updated'

        return True

    def remove(self, repo: Union[CatCodeRepoEntry, list[CatCodeRepoEntry]]):
        if isinstance(repo, list):
            for r in repo:
                self.remove(r)
        else:
            if repo.name in self._cache.keys():
                del self._cache[repo.name]
            else:
                logger.warning(f'File with id "{repo.name}" does not exist')
    def get_all(self):
        return self._cache



tracked_paths = TrackedPathsCache()
cache = ComponentCache(BASE_DIR)