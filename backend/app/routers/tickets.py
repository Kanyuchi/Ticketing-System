import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.admin_user import AdminUser
from app.models.ticket_type import TicketType
from app.routers.auth import get_current_admin
from app.schemas.ticket_type import TicketTypeCreate, TicketTypeOut, TicketTypeUpdate

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("/types", response_model=list[TicketTypeOut])
async def list_ticket_types(db: AsyncSession = Depends(get_db)):
    """Public: list all active ticket types."""
    result = await db.execute(
        select(TicketType).where(TicketType.is_active == True).order_by(TicketType.sort_order)
    )
    return result.scalars().all()


@router.get("/types/all", response_model=list[TicketTypeOut])
async def list_all_ticket_types(
    admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)
):
    """Admin: list all ticket types including inactive."""
    result = await db.execute(select(TicketType).order_by(TicketType.sort_order))
    return result.scalars().all()


@router.post("/types", response_model=TicketTypeOut, status_code=201)
async def create_ticket_type(
    data: TicketTypeCreate,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    ticket_type = TicketType(**data.model_dump())
    db.add(ticket_type)
    await db.flush()
    await db.refresh(ticket_type)
    return ticket_type


@router.patch("/types/{type_id}", response_model=TicketTypeOut)
async def update_ticket_type(
    type_id: uuid.UUID,
    data: TicketTypeUpdate,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(TicketType).where(TicketType.id == type_id))
    ticket_type = result.scalar_one_or_none()
    if not ticket_type:
        raise HTTPException(status_code=404, detail="Ticket type not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(ticket_type, field, value)

    await db.flush()
    await db.refresh(ticket_type)
    return ticket_type
