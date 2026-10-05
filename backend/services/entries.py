from datetime import date
from uuid import UUID

from db import entries as entries_db
from db import pits as pits_db
from errors import ApiError
from models.entries import (
    Entry,
    EntryCreate,
    EntryNumbersUpdate,
    EntryStatus,
    EntryStatusUpdate,
)

# Workflow: draft -> submitted -> approved, and a supervisor may send a submitted
# entry back to draft. Approved is final, so it is nobody's allowed source.
# Maps each target status to the statuses an entry may move to it from.
_ALLOWED_FROM: dict[EntryStatus, tuple[EntryStatus, ...]] = {
    "submitted": ("draft",),
    "approved": ("submitted",),
    "draft": ("submitted",),
}


def _entry_not_found(entry_id: UUID) -> ApiError:
    return ApiError(
        code="ENTRY_NOT_FOUND",
        message=f"Entry {entry_id} does not exist",
        status_code=404,
    )


def _entry_locked() -> ApiError:
    return ApiError(
        code="ENTRY_LOCKED",
        message="Entry is approved and locked; it can no longer be changed",
        status_code=409,
    )


async def list_entries(
    status: EntryStatus | None, pit_id: UUID | None
) -> list[Entry]:
    return await entries_db.list_entries(status, pit_id)


async def get_entry(entry_id: UUID) -> Entry:
    entry = await entries_db.get_entry(entry_id)
    if entry is None:
        raise _entry_not_found(entry_id)
    return entry


async def create_entry(payload: EntryCreate) -> Entry:
    if payload.report_date > date.today():
        raise ApiError(
            code="REPORT_DATE_IN_FUTURE",
            message="Report date cannot be in the future",
            status_code=422,
        )
    if not await pits_db.pit_exists(payload.pit_id):
        raise ApiError(
            code="PIT_NOT_FOUND",
            message=f"Pit {payload.pit_id} does not exist",
            status_code=422,
        )
    entry = await entries_db.insert_entry(payload)
    if entry is None:
        raise ApiError(
            code="DUPLICATE_ENTRY",
            message=(
                f"This pit already has a {payload.shift} shift {payload.material} "
                f"entry for {payload.report_date}"
            ),
            status_code=409,
        )
    return entry


async def correct_entry_numbers(
    entry_id: UUID, payload: EntryNumbersUpdate
) -> Entry:
    entry = await entries_db.update_entry_numbers(
        entry_id, payload.planned_tonnes, payload.actual_tonnes
    )
    if entry is not None:
        return entry
    # The guarded UPDATE matched nothing: the entry is missing or approved.
    if await entries_db.get_entry(entry_id) is None:
        raise _entry_not_found(entry_id)
    raise _entry_locked()


async def change_entry_status(
    entry_id: UUID, payload: EntryStatusUpdate
) -> Entry:
    target = payload.status
    entry = await entries_db.update_entry_status(
        entry_id, target, _ALLOWED_FROM[target]
    )
    if entry is not None:
        return entry
    # The guarded UPDATE matched nothing; look at the entry to say why.
    current = await entries_db.get_entry(entry_id)
    if current is None:
        raise _entry_not_found(entry_id)
    if current.status == "approved":
        raise _entry_locked()
    raise ApiError(
        code="INVALID_STATUS_TRANSITION",
        message=f"Cannot move an entry from {current.status} to {target}",
        status_code=409,
    )
