from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class StatusCounts(BaseModel):
    draft: int
    submitted: int
    approved: int


class MaterialTotals(BaseModel):
    planned_tonnes: float
    actual_tonnes: float
    variance_tonnes: float = Field(
        description="actual - planned; negative means behind plan"
    )
    achievement_pct: float | None = Field(
        description="actual / planned * 100; null when nothing was planned"
    )


class ProductionTotals(BaseModel):
    entry_count: int
    status_counts: StatusCounts
    ore: MaterialTotals
    overburden: MaterialTotals
    planned_stripping_ratio: float | None = Field(
        description="Planned overburden tonnes per ore tonne; null without ore"
    )
    actual_stripping_ratio: float | None = Field(
        description="Actual overburden tonnes per ore tonne; null without ore"
    )


class PitSummary(BaseModel):
    pit_id: UUID
    pit_name: str
    totals: ProductionTotals


class Summary(BaseModel):
    date_from: date | None
    date_to: date | None
    totals: ProductionTotals
    pits: list[PitSummary]
