from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.admin_user import AdminUser
from app.routers.auth import get_current_admin
from app.services.rewards_service import check_and_apply_rewards, get_referral_reward_status, REWARD_TIERS

router = APIRouter(prefix="/rewards", tags=["rewards"])


@router.post("/check")
async def check_rewards(
    referral_code: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Check and apply referral reward for a code (called after order attribution)."""
    result = await check_and_apply_rewards(db, referral_code)
    if not result:
        return {"reward": None, "message": "No reward tier reached yet"}
    return {"reward": result}


@router.get("/status")
async def reward_status(
    referral_code: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Get current reward tier status for a referral code."""
    try:
        return await get_referral_reward_status(db, referral_code)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/tiers")
async def list_tiers():
    """Public: list reward tier thresholds."""
    return {"tiers": REWARD_TIERS}
