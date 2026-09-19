from fastapi import APIRouter

from db.health import check_db
from errors import ApiError
from models.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    try:
        db_version = await check_db()
    except Exception as exc:
        raise ApiError(
            code="DB_UNAVAILABLE",
            message="Database is not reachable",
            status_code=503,
        ) from exc
    return HealthResponse(status="ok", db_version=db_version)
