import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.admin_user import AdminUser
from app.routers.auth import get_current_admin
from app.schemas.referral import ReferralCreate, ReferralOut, ReferralStatsOut
from app.services.referral_service import (
    attribute_order,
    create_referral,
    get_referral_by_code,
    get_referral_stats,
    list_referrals,
    track_click,
)

router = APIRouter(prefix="/referrals", tags=["referrals"])


@router.post("", response_model=ReferralOut, status_code=201)
async def create(
    data: ReferralCreate,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: create a referral code for an ambassador."""
    try:
        referral = await create_referral(db, data.owner_name, data.owner_email, data.code)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return referral


@router.get("", response_model=list[ReferralOut])
async def list_all(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: list all referrals sorted by revenue."""
    return await list_referrals(db)


@router.get("/leaderboard", response_model=list[ReferralStatsOut])
async def leaderboard(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: referral performance leaderboard."""
    refs = await list_referrals(db)
    return [
        {
            "id": r.id,
            "code": r.code,
            "owner_name": r.owner_name,
            "owner_email": r.owner_email,
            "clicks": r.clicks,
            "orders_count": r.orders_count,
            "revenue_eur": r.revenue_eur,
            "conversion_rate": r.orders_count / r.clicks if r.clicks > 0 else 0.0,
        }
        for r in refs
    ]


@router.get("/track/{code}")
async def track(code: str, db: AsyncSession = Depends(get_db)):
    """Public: track a referral click and redirect to ticket page."""
    referral = await track_click(db, code)
    if not referral:
        raise HTTPException(status_code=404, detail="Referral code not found")
    return RedirectResponse(url=f"{settings.frontend_url}?ref={code}", status_code=302)


@router.post("/attribute")
async def attribute(
    referral_code: str = Query(...),
    order_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Public: attribute an order to a referral code (called after order creation)."""
    success = await attribute_order(db, referral_code, order_id)
    if not success:
        raise HTTPException(status_code=400, detail="Could not attribute order")
    return {"attributed": True}


@router.get("/{referral_id}/stats", response_model=ReferralStatsOut)
async def stats(
    referral_id: uuid.UUID,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: get detailed stats for a referral."""
    try:
        return await get_referral_stats(db, referral_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
