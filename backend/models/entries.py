from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

EntryStatus = Literal["draft", "submitted", "approved"]
Shift = Literal["day", "night"]
Material = Literal["ore", "overburden"]

# Mirrors the NUMERIC(12, 2) columns, so excess precision is rejected, not rounded.
Tonnes = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]


class EntryCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pit_id: UUID
    report_date: date
    shift: Shift
    material: Material
    planned_tonnes: Tonnes
    actual_tonnes: Tonnes


class EntryNumbersUpdate(BaseModel):
    """Corrects an entry's numbers; an omitted field keeps its current value."""

    model_config = ConfigDict(extra="forbid")

    planned_tonnes: Tonnes | None = None
    actual_tonnes: Tonnes | None = None

    @model_validator(mode="after")
    def require_a_number(self) -> "EntryNumbersUpdate":
        if self.planned_tonnes is None and self.actual_tonnes is None:
            raise ValueError("Provide planned_tonnes and/or actual_tonnes")
        return self


class EntryStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: EntryStatus


class Entry(BaseModel):
    id: UUID
    pit_id: UUID
    pit_name: str
    report_date: date
    shift: Shift
    material: Material
    planned_tonnes: float
    actual_tonnes: float
    status: EntryStatus
    created_at: datetime
    updated_at: datetime
