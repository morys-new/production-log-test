from collections.abc import Sequence
from decimal import Decimal
from uuid import UUID

from db.client import get_pool
from models.entries import Entry, EntryCreate, EntryStatus

# Queries alias the entry "e" and its pit "p". INSERT/UPDATE wrap RETURNING in a
# CTE named "e", so every function returns the same shape as a SELECT.
_ENTRY_COLUMNS = """
    e.id, e.pit_id, p.name AS pit_name, e.report_date, e.shift, e.material,
    e.planned_tonnes, e.actual_tonnes, e.status, e.created_at, e.updated_at
"""


async def list_entries(
    status: EntryStatus | None, pit_id: UUID | None
) -> list[Entry]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            f"""
            SELECT {_ENTRY_COLUMNS}
            FROM production_entries e
            JOIN pits p ON p.id = e.pit_id
            WHERE ($1::text IS NULL OR e.status = $1)
              AND ($2::uuid IS NULL OR e.pit_id = $2)
            ORDER BY e.report_date DESC, lower(p.name), e.shift, e.material
            """,
            status,
            pit_id,
        )
    return [Entry.model_validate(dict(row)) for row in rows]


async def get_entry(entry_id: UUID) -> Entry | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            f"""
            SELECT {_ENTRY_COLUMNS}
            FROM production_entries e
            JOIN pits p ON p.id = e.pit_id
            WHERE e.id = $1
            """,
            entry_id,
        )
    return None if row is None else Entry.model_validate(dict(row))


async def insert_entry(entry: EntryCreate) -> Entry | None:
    """Insert a draft entry; None when the pit already has an entry for that
    report date, shift and material."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            f"""
            WITH e AS (
                INSERT INTO production_entries (
                    pit_id, report_date, shift, material,
                    planned_tonnes, actual_tonnes
                )
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT ON CONSTRAINT
                    production_entries_pit_date_shift_material_key DO NOTHING
                RETURNING *
            )
            SELECT {_ENTRY_COLUMNS} FROM e JOIN pits p ON p.id = e.pit_id
            """,
            entry.pit_id,
            entry.report_date,
            entry.shift,
            entry.material,
            entry.planned_tonnes,
            entry.actual_tonnes,
        )
    return None if row is None else Entry.model_validate(dict(row))


async def update_entry_numbers(
    entry_id: UUID, planned_tonnes: Decimal | None, actual_tonnes: Decimal | None
) -> Entry | None:
    """Update the given numbers (None keeps the current value) in one statement
    that skips approved entries; None when the entry is missing or approved."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            f"""
            WITH e AS (
                UPDATE production_entries
                SET planned_tonnes = COALESCE($2, planned_tonnes),
                    actual_tonnes = COALESCE($3, actual_tonnes)
                WHERE id = $1 AND status <> 'approved'
                RETURNING *
            )
            SELECT {_ENTRY_COLUMNS} FROM e JOIN pits p ON p.id = e.pit_id
            """,
            entry_id,
            planned_tonnes,
            actual_tonnes,
        )
    return None if row is None else Entry.model_validate(dict(row))


async def update_entry_status(
    entry_id: UUID, new_status: EntryStatus, from_statuses: Sequence[EntryStatus]
) -> Entry | None:
    """Set new_status only if the current status is in from_statuses, checked in
    the same statement; None when the entry is missing or not in those statuses."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            f"""
            WITH e AS (
                UPDATE production_entries
                SET status = $2
                WHERE id = $1 AND status = ANY($3::text[])
                RETURNING *
            )
            SELECT {_ENTRY_COLUMNS} FROM e JOIN pits p ON p.id = e.pit_id
            """,
            entry_id,
            new_status,
            list(from_statuses),
        )
    return None if row is None else Entry.model_validate(dict(row))
