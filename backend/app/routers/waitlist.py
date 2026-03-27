import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.admin_user import AdminUser
from app.routers.auth import get_current_admin
from app.schemas.waitlist import WaitlistJoin, WaitlistOut
from app.services.waitlist_service import join_waitlist, leave_waitlist, list_waitlist, notify_next_in_line

router = APIRouter(prefix="/waitlist", tags=["waitlist"])


@router.post("", response_model=WaitlistOut, status_code=201)
async def join(
    data: WaitlistJoin,
    db: AsyncSession = Depends(get_db),
):
    """Public: join the waitlist for a sold-out ticket type."""
    try:
        entry = await join_waitlist(db, data.ticket_type_id, data.email, data.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Build response with ticket type name
    entries = await list_waitlist(db, data.ticket_type_id)
    for e in entries:
        if e["id"] == entry.id:
            return e
    raise HTTPException(status_code=500, detail="Entry created but could not retrieve")


@router.delete("/{entry_id}", status_code=204)
async def leave(
    entry_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Public: leave the waitlist."""
    success = await leave_waitlist(db, entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Waitlist entry not found")


@router.get("", response_model=list[WaitlistOut])
async def list_entries(
    ticket_type_id: uuid.UUID | None = Query(None),
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: list waitlist entries."""
    return await list_waitlist(db, ticket_type_id)


@router.post("/notify/{ticket_type_id}")
async def notify(
    ticket_type_id: uuid.UUID,
    count: int = Query(1, ge=1, le=50),
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: notify next N people on waitlist when spots open."""
    entries = await notify_next_in_line(db, ticket_type_id, count)
    return {
        "notified": len(entries),
        "emails": [e.email for e in entries],
    }
