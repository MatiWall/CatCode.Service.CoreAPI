from dataclasses import dataclass
from pathlib import Path
from extensions.configuration import read_configs_to_dataclass, hosting_environment
from extensions.opentelemetry.config import configure_opentelemetry

BASE_DIR = Path(__file__).parent




@dataclass
class Config:
   username:str
   rabbitmq_url: str
   logging_level: str
   etcd_host: str
   github_token: str = ''

config = read_configs_to_dataclass(Config, BASE_DIR)

configure_opentelemetry(
   enable_otel=hosting_environment.is_production(),
   level=config.logging_level
)
