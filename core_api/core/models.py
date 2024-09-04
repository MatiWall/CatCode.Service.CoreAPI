import uuid
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict





class Metadata(BaseModel):
    deployable_unit: str = Field(alias='deployableUnit')
    application: str
    system: str
    description: str = ''
    tags: list[str] = []
    labels: dict = Field(default_factory=dict)
    annotations: dict = Field(default_factory=dict)
    links: Optional[list[dict]] = Field(default_factory=list)
    uid: str = Field(default_factory=lambda: str(uuid.uuid4()))

    model_config = ConfigDict(populate_by_name=True)  # (1)!


class Spec(BaseModel):
    type: str
    issues: Optional[list[dict]] = Field(default_factory=list)
    plugins: Optional[list[dict]] = Field(default_factory=list)
    dependencies: list = Field(default_factory=list)
    lifecycle: str = ''
    owner: str


class Application(BaseModel):
    kind: str
    metadata: Metadata
    spec: Spec
