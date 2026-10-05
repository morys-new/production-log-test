from datetime import date

from fastapi import APIRouter

from models.summary import Summary
from services import summary as summary_service

router = APIRouter(tags=["summary"])


@router.get("/summary", response_model=Summary)
async def get_summary(
    date_from: date | None = None, date_to: date | None = None
) -> Summary:
    """Planned vs actual tonnes per material, achievement %, stripping ratio and
    status counts, overall and per pit, for an optional inclusive date range.
    Totals include entries in every status; status_counts shows how many are
    not yet approved. Pits without entries are listed with zeros."""
    return await summary_service.get_summary(date_from, date_to)
