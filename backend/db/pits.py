from uuid import UUID

from db.client import get_pool
from models.pits import Pit

_PIT_COLUMNS = "id, name, created_at"


async def list_pits() -> list[Pit]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            f"SELECT {_PIT_COLUMNS} FROM pits ORDER BY lower(name)"
        )
    return [Pit.model_validate(dict(row)) for row in rows]


async def insert_pit(name: str) -> Pit | None:
    """Insert a pit; None when the name is already taken (case-insensitive)."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            f"""
            INSERT INTO pits (name) VALUES ($1)
            ON CONFLICT ((lower(name))) DO NOTHING
            RETURNING {_PIT_COLUMNS}
            """,
            name,
        )
    return None if row is None else Pit.model_validate(dict(row))


async def pit_exists(pit_id: UUID) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        exists: object = await conn.fetchval(
            "SELECT EXISTS (SELECT 1 FROM pits WHERE id = $1)", pit_id
        )
    return exists is True
