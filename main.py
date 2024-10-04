import asyncio
import json
import logging
from contextlib import asynccontextmanager

import yaml

from core_api.etcd import run_command
from core_api.etcd.keys import key_builder
from settings import BASE_DIR, config

logger = logging.getLogger(__name__)


from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import uvicorn

from core_api.api.etcd import router as etcd_router

@asynccontextmanager
async def initialize_resource_definition_cache(app: FastAPI):

    yield

app = FastAPI(
    root_path='/api/core-api',
    # openapi_url="/api/core-api/openapi.json",
    lifespan=initialize_resource_definition_cache
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

@app.get("/health/live")
async def liveness_check():
    return JSONResponse(content={"status": "alive"}, status_code=200)

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
    logger.info(f'Connecting to etcd running on {config.etcd_host}')
    uvicorn.run('main:app', host='0.0.0.0')
