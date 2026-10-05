from dataclasses import dataclass, fields
from datetime import date
from decimal import Decimal
from uuid import UUID

import asyncpg

from db.client import get_pool


@dataclass(frozen=True)
class Aggregates:
    entry_count: int
    draft_count: int
    submitted_count: int
    approved_count: int
    ore_planned: Decimal
    ore_actual: Decimal
    overburden_planned: Decimal
    overburden_actual: Decimal


@dataclass(frozen=True)
class PitAggregates:
    pit_id: UUID
    pit_name: str
    aggregates: Aggregates


@dataclass(frozen=True)
class SummaryData:
    overall: Aggregates
    pits: list[PitAggregates]


# Column names match the Aggregates fields. count(e.id) and COALESCE keep a pit
# without entries at zero instead of NULL.
_AGGREGATES = """
    count(e.id) AS entry_count,
    count(e.id) FILTER (WHERE e.status = 'draft') AS draft_count,
    count(e.id) FILTER (WHERE e.status = 'submitted') AS submitted_count,
    count(e.id) FILTER (WHERE e.status = 'approved') AS approved_count,
    COALESCE(SUM(e.planned_tonnes) FILTER (WHERE e.material = 'ore'), 0)
        AS ore_planned,
    COALESCE(SUM(e.actual_tonnes) FILTER (WHERE e.material = 'ore'), 0)
        AS ore_actual,
    COALESCE(SUM(e.planned_tonnes) FILTER (WHERE e.material = 'overburden'), 0)
        AS overburden_planned,
    COALESCE(SUM(e.actual_tonnes) FILTER (WHERE e.material = 'overburden'), 0)
        AS overburden_actual
"""

# $1 = date_from, $2 = date_to; either may be NULL for an open-ended period.
_IN_PERIOD = """
    ($1::date IS NULL OR e.report_date >= $1)
    AND ($2::date IS NULL OR e.report_date <= $2)
"""


def _aggregates(row: asyncpg.Record) -> Aggregates:
    return Aggregates(**{field.name: row[field.name] for field in fields(Aggregates)})


async def load_summary(date_from: date | None, date_to: date | None) -> SummaryData:
    """Overall and per-pit aggregates for the period. Both queries read one
    snapshot, so the overall figures always equal the sum of the pits."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction(isolation="repeatable_read", readonly=True):
            overall = await conn.fetchrow(
                f"SELECT {_AGGREGATES} FROM production_entries e WHERE {_IN_PERIOD}",
                date_from,
                date_to,
            )
            pit_rows = await conn.fetch(
                f"""
                SELECT p.id AS pit_id, p.name AS pit_name, {_AGGREGATES}
                FROM pits p
                LEFT JOIN production_entries e
                    ON e.pit_id = p.id AND {_IN_PERIOD}
                GROUP BY p.id, p.name
                ORDER BY lower(p.name)
                """,
                date_from,
                date_to,
            )
    # An aggregate query without GROUP BY always returns exactly one row.
    assert overall is not None
    return SummaryData(
        overall=_aggregates(overall),
        pits=[
            PitAggregates(
                pit_id=row["pit_id"],
                pit_name=row["pit_name"],
                aggregates=_aggregates(row),
            )
            for row in pit_rows
        ],
    )
