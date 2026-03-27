import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.admin_user import AdminUser
from app.routers.auth import get_current_admin
from app.schemas.checkin import CheckInBatchRequest, CheckInOut, CheckInRequest, CheckInStats
from app.services.checkin_service import (
    batch_sync_checkins,
    check_in_order,
    get_checkin_by_order,
    get_checkin_stats,
    list_checkins,
)

router = APIRouter(prefix="/checkin", tags=["check-in"])


@router.post("", response_model=CheckInOut, status_code=201)
async def perform_checkin(
    data: CheckInRequest,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: check in an attendee by order ID."""
    try:
        checkin = await check_in_order(
            db,
            order_id=data.order_id,
            checked_in_by=admin.email,
            device_id=data.device_id,
            notes=data.notes,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Build response with order details
    entries = await list_checkins(db)
    for entry in entries:
        if entry["order_id"] == checkin.order_id:
            return entry
    raise HTTPException(status_code=500, detail="Check-in created but could not retrieve")


@router.post("/batch", status_code=200)
async def batch_checkin(
    data: CheckInBatchRequest,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: sync a batch of offline check-ins."""
    entries = [
        {
            "order_id": e.order_id,
            "device_id": e.device_id,
            "checked_in_at": e.checked_in_at,
            "notes": e.notes,
        }
        for e in data.entries
    ]
    results = await batch_sync_checkins(db, entries, checked_in_by=admin.email)
    return {"results": results}


@router.get("", response_model=list[CheckInOut])
async def list_all(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: list all check-ins."""
    return await list_checkins(db)


@router.get("/stats", response_model=CheckInStats)
async def stats(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: check-in rate stats."""
    return await get_checkin_stats(db)


@router.get("/verify/{order_id}")
async def verify(
    order_id: uuid.UUID,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: check if an order has been checked in."""
    checkin = await get_checkin_by_order(db, order_id)
    if checkin:
        return {"checked_in": True, "checked_in_at": checkin.checked_in_at}
    return {"checked_in": False}
