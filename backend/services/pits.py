from db import pits as pits_db
from errors import ApiError
from models.pits import Pit, PitCreate


async def list_pits() -> list[Pit]:
    return await pits_db.list_pits()


async def create_pit(payload: PitCreate) -> Pit:
    pit = await pits_db.insert_pit(payload.name)
    if pit is None:
        raise ApiError(
            code="PIT_NAME_TAKEN",
            message=f"A pit named '{payload.name}' already exists",
            status_code=409,
        )
    return pit
