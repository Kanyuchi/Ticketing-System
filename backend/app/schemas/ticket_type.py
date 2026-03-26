import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.ticket_type import TicketCategory


class TicketTypeCreate(BaseModel):
    name: str
    category: TicketCategory
    description: str | None = None
    price_eur: int = 0  # cents
    is_complimentary: bool = False
    requires_application: bool = False
    quantity_total: int | None = None
    sort_order: int = 0


class TicketTypeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price_eur: int | None = None
    is_complimentary: bool | None = None
    requires_application: bool | None = None
    quantity_total: int | None = None
    is_active: bool | None = None
    sort_order: int | None = None


class TicketTypeOut(BaseModel):
    id: uuid.UUID
    name: str
    category: TicketCategory
    description: str | None
    price_eur: int
    is_complimentary: bool
    requires_application: bool
    quantity_total: int | None
    quantity_sold: int
    is_active: bool
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}
