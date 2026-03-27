import csv
import io
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.admin_user import AdminUser
from app.models.attendee import Attendee
from app.models.order import Order, OrderStatus, PaymentStatus
from app.models.ticket_type import TicketType
from app.routers.auth import get_current_admin
from app.schemas.order import OrderCreate, OrderOut
from app.services.order_service import create_order, get_order

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderOut, status_code=201)
async def place_order(data: OrderCreate, db: AsyncSession = Depends(get_db)):
    """Public: create a new order."""
    try:
        order = await create_order(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Attribute to referral if provided
    if data.referral_code:
        from app.services.referral_service import attribute_order
        await attribute_order(db, data.referral_code, order.id)

    # Sync to Google Sheets (fire and forget)
    from app.services.sheets_service import sync_order_to_sheet
    ticket_type_name = "Unknown"
    if order.items:
        result = await db.execute(
            select(TicketType).where(TicketType.id == order.items[0].ticket_type_id)
        )
        tt = result.scalar_one_or_none()
        if tt:
            ticket_type_name = tt.name
    sync_order_to_sheet(
        order.order_number, order.attendee.name, order.attendee.email,
        ticket_type_name, order.total_eur, order.payment_status.value, order.status.value,
    )

    return order


@router.get("/{order_id}", response_model=OrderOut)
async def get_order_detail(order_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    order = await get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("", response_model=list[OrderOut])
async def list_orders(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    voucher_code: str | None = Query(None),
    name: str | None = Query(None),
    email: str | None = Query(None),
    company: str | None = Query(None),
    order_status: OrderStatus | None = Query(None),
    payment_status: PaymentStatus | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """Admin: list orders with filters."""
    query = (
        select(Order)
        .join(Attendee)
        .options(selectinload(Order.attendee), selectinload(Order.items))
        .order_by(Order.created_at.desc())
    )

    if voucher_code:
        query = query.where(Order.voucher_code.ilike(f"%{voucher_code}%"))
    if name:
        query = query.where(Attendee.name.ilike(f"%{name}%"))
    if email:
        query = query.where(Attendee.email.ilike(f"%{email}%"))
    if company:
        query = query.where(Attendee.company.ilike(f"%{company}%"))
    if order_status:
        query = query.where(Order.status == order_status)
    if payment_status:
        query = query.where(Order.payment_status == payment_status)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{order_id}/invoice")
async def download_invoice(order_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Public: download PDF invoice for a confirmed order."""
    from app.services.invoice_service import generate_invoice_pdf
    try:
        pdf_bytes = await generate_invoice_pdf(db, order_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=invoice-{order_id}.pdf"},
    )


@router.get("/export/csv")
async def export_orders_csv(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    voucher_code: str | None = Query(None),
    name: str | None = Query(None),
    email: str | None = Query(None),
    company: str | None = Query(None),
    order_status: OrderStatus | None = Query(None),
    payment_status: PaymentStatus | None = Query(None),
):
    """Admin: export filtered orders as CSV."""
    query = (
        select(Order)
        .join(Attendee)
        .options(selectinload(Order.attendee), selectinload(Order.items))
        .order_by(Order.created_at.desc())
    )

    if voucher_code:
        query = query.where(Order.voucher_code.ilike(f"%{voucher_code}%"))
    if name:
        query = query.where(Attendee.name.ilike(f"%{name}%"))
    if email:
        query = query.where(Attendee.email.ilike(f"%{email}%"))
    if company:
        query = query.where(Attendee.company.ilike(f"%{company}%"))
    if order_status:
        query = query.where(Order.status == order_status)
    if payment_status:
        query = query.where(Order.payment_status == payment_status)

    result = await db.execute(query)
    orders = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Order Number", "Name", "Email", "Company", "Title",
        "Voucher Code", "Order Status", "Payment Status", "Total (EUR)", "Created At",
    ])
    for order in orders:
        writer.writerow([
            order.order_number,
            order.attendee.name,
            order.attendee.email,
            order.attendee.company or "",
            order.attendee.title or "",
            order.voucher_code or "",
            order.status.value,
            order.payment_status.value,
            f"{order.total_eur / 100:.2f}",
            order.created_at.isoformat(),
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=orders.csv"},
    )
