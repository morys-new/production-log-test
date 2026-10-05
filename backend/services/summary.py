from datetime import date
from decimal import Decimal

from db import summary as summary_db
from errors import ApiError
from models.summary import (
    MaterialTotals,
    PitSummary,
    ProductionTotals,
    StatusCounts,
    Summary,
)


def _achievement_pct(actual: Decimal, planned: Decimal) -> float | None:
    if planned == 0:
        return None
    return round(float(actual / planned * 100), 1)


def _stripping_ratio(overburden: Decimal, ore: Decimal) -> float | None:
    if ore == 0:
        return None
    return round(float(overburden / ore), 2)


def _material_totals(planned: Decimal, actual: Decimal) -> MaterialTotals:
    return MaterialTotals(
        planned_tonnes=float(planned),
        actual_tonnes=float(actual),
        variance_tonnes=float(actual - planned),
        achievement_pct=_achievement_pct(actual, planned),
    )


def _production_totals(agg: summary_db.Aggregates) -> ProductionTotals:
    return ProductionTotals(
        entry_count=agg.entry_count,
        status_counts=StatusCounts(
            draft=agg.draft_count,
            submitted=agg.submitted_count,
            approved=agg.approved_count,
        ),
        ore=_material_totals(agg.ore_planned, agg.ore_actual),
        overburden=_material_totals(agg.overburden_planned, agg.overburden_actual),
        planned_stripping_ratio=_stripping_ratio(
            agg.overburden_planned, agg.ore_planned
        ),
        actual_stripping_ratio=_stripping_ratio(
            agg.overburden_actual, agg.ore_actual
        ),
    )


async def get_summary(date_from: date | None, date_to: date | None) -> Summary:
    if date_from is not None and date_to is not None and date_from > date_to:
        raise ApiError(
            code="INVALID_DATE_RANGE",
            message="date_from must be on or before date_to",
            status_code=422,
        )
    data = await summary_db.load_summary(date_from, date_to)
    return Summary(
        date_from=date_from,
        date_to=date_to,
        totals=_production_totals(data.overall),
        pits=[
            PitSummary(
                pit_id=pit.pit_id,
                pit_name=pit.pit_name,
                totals=_production_totals(pit.aggregates),
            )
            for pit in data.pits
        ],
    )
