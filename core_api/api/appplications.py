from pydantic import BaseModel
from fastapi import APIRouter

from core_api.core.componentcache import cache
from core_api.core.models import Metadata, Application


router = APIRouter(prefix='/catalog')





class ApplicationCatalog(BaseModel):
    apps: list[Metadata]

class Applications(BaseModel):
    apps: list[Application]

@router.get('')
def get_applications():
    configs = cache.get()

    apps = []
    for config in configs:
        apps.append(config)

    return Applications(apps=apps)


@router.get('/{system}/{application}/{deployableunit}')
def get_applications(system: str, application: str, deployableunit: str):
    config = cache.get((system, application, deployableunit))

    return config
