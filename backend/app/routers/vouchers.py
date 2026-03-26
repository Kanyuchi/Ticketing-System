import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.admin_user import AdminUser
from app.routers.auth import get_current_admin
from app.schemas.voucher import VoucherBulkCreate, VoucherOut
from app.services.voucher_service import bulk_create_vouchers, get_voucher_by_code, list_vouchers

router = APIRouter(prefix="/vouchers", tags=["vouchers"])


@router.post("/bulk", response_model=list[VoucherOut], status_code=201)
async def create_vouchers_bulk(
    data: VoucherBulkCreate,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: bulk create voucher codes for a ticket type."""
    vouchers = await bulk_create_vouchers(db, data.ticket_type_id, data.prefix, data.count)
    return vouchers


@router.get("", response_model=list[VoucherOut])
async def list_all_vouchers(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    ticket_type_id: uuid.UUID | None = Query(None),
):
    """Admin: list vouchers, optionally filtered by ticket type."""
    return await list_vouchers(db, ticket_type_id)


@router.get("/validate/{code}")
async def validate_voucher(code: str, db: AsyncSession = Depends(get_db)):
    """Public: check if a voucher code is valid."""
    voucher = await get_voucher_by_code(db, code)
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found")
    if voucher.is_used:
        raise HTTPException(status_code=400, detail="Voucher already used")
    return {"valid": True, "ticket_type_id": str(voucher.ticket_type_id)}
