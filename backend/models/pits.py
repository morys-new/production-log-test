from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints

PitName = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
]


class PitCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: PitName


class Pit(BaseModel):
    id: UUID
    name: str
    created_at: datetime
