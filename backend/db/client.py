import asyncpg

_pool: asyncpg.Pool[asyncpg.Record] | None = None


async def create_pool(database_url: str) -> None:
    global _pool
    _pool = await asyncpg.create_pool(database_url)


async def get_pool() -> asyncpg.Pool[asyncpg.Record]:
    if _pool is None:
        raise RuntimeError("Database pool has not been initialised")
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
