from uuid import UUID

from fastapi import APIRouter

from models.entries import (
    Entry,
    EntryCreate,
    EntryNumbersUpdate,
    EntryStatus,
    EntryStatusUpdate,
)
from services import entries as entries_service

router = APIRouter(tags=["entries"])


@router.get("/entries", response_model=list[Entry])
async def list_entries(
    status: EntryStatus | None = None, pit_id: UUID | None = None
) -> list[Entry]:
    """Newest report date first. Both filters are optional and combinable."""
    return await entries_service.list_entries(status, pit_id)


@router.post("/entries", response_model=Entry, status_code=201)
async def create_entry(payload: EntryCreate) -> Entry:
    """New entries start as draft."""
    return await entries_service.create_entry(payload)


@router.get("/entries/{entry_id}", response_model=Entry)
async def get_entry(entry_id: UUID) -> Entry:
    return await entries_service.get_entry(entry_id)


@router.patch("/entries/{entry_id}", response_model=Entry)
async def correct_entry_numbers(
    entry_id: UUID, payload: EntryNumbersUpdate
) -> Entry:
    """Correct planned/actual tonnes while the entry is not yet approved."""
    return await entries_service.correct_entry_numbers(entry_id, payload)


@router.patch("/entries/{entry_id}/status", response_model=Entry)
async def change_entry_status(
    entry_id: UUID, payload: EntryStatusUpdate
) -> Entry:
    """Allowed: draft -> submitted, submitted -> approved, submitted -> draft.
    Approved entries are locked."""
    return await entries_service.change_entry_status(entry_id, payload)
