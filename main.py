import asyncio
import logging
from contextlib import asynccontextmanager

from core_api.etcd.cache import resource_definition_cache

logger = logging.getLogger(__name__)

from starlette.middleware.base import BaseHTTPMiddleware

from core_api.core.startup import on_start_up

from core_api import scheduler

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import uvicorn

from core_api.api.appplications import router as application_router
from core_api.api.statistics import router as stat_router
from core_api.api.etcd import router as etcd_router

@asynccontextmanager
async def initialize_resource_definition_cache():
    # resource_definitions = fetch_resource_definitions(f'registry/api.catcode.io/resourcedefinition')
    #
    # for resource_definition in resource_definitions:
    #     resource_definition_cache.add(resource_definition)

    yield

app = FastAPI(
    root_path='/api/core-api/v1',
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logging.error(f"{request}: {exc_str}")
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


# Allow all origins, allow all methods, allow all headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.on_event("startup")
# async def startup_event():
#     await on_start_up()
#     scheduler.start()


#app.include_router(application_router)
#app.include_router(stat_router)
app.include_router(etcd_router)
if __name__ == '__main__':
    logging.getLogger("pika").setLevel(logging.ERROR)
    logging.getLogger("aiormq").setLevel(logging.ERROR)
    logging.getLogger("aio_pika").setLevel(logging.ERROR)
    logging.getLogger("httpcore").setLevel(logging.ERROR)
    logging.getLogger("httpx").setLevel(logging.ERROR)

    logger.info('CatCode core core_api starting up')
    uvicorn.run('main:app', host='0.0.0.0')
