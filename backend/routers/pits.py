from fastapi import APIRouter

from models.pits import Pit, PitCreate
from services import pits as pits_service

router = APIRouter(tags=["pits"])


@router.get("/pits", response_model=list[Pit])
async def list_pits() -> list[Pit]:
    return await pits_service.list_pits()


@router.post("/pits", response_model=Pit, status_code=201)
async def create_pit(payload: PitCreate) -> Pit:
    return await pits_service.create_pit(payload)
