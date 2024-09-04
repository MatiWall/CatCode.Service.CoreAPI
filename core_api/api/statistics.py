
from fastapi import APIRouter
from core_api.core.componentcache import cache


router = APIRouter(prefix='/statistics')

@router.get('/')
def get_applications():
    config = cache.stats()

    return config