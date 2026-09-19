from db.client import get_pool


async def check_db() -> str:
    pool = await get_pool()
    async with pool.acquire() as conn:
        result: object = await conn.fetchval("SELECT version()")
    return str(result)
