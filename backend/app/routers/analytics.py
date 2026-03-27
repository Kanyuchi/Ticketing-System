from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.admin_user import AdminUser
from app.routers.auth import get_current_admin
from app.schemas.analytics import AnalyticsDashboard, ConversionFunnel, SalesByType, RevenueOverTime, TopReferrer
from app.services.analytics_service import (
    get_conversion_funnel,
    get_dashboard,
    get_revenue_over_time,
    get_sales_by_type,
    get_top_referrers,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=AnalyticsDashboard)
async def dashboard(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: full analytics dashboard."""
    return await get_dashboard(db)


@router.get("/sales", response_model=list[SalesByType])
async def sales_by_type(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: sales breakdown by ticket type."""
    return await get_sales_by_type(db)


@router.get("/revenue", response_model=list[RevenueOverTime])
async def revenue_over_time(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: daily revenue chart data."""
    return await get_revenue_over_time(db)


@router.get("/funnel", response_model=ConversionFunnel)
async def funnel(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: conversion funnel metrics."""
    return await get_conversion_funnel(db)


@router.get("/referrers", response_model=list[TopReferrer])
async def top_referrers(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: top performing referrers."""
    return await get_top_referrers(db)
