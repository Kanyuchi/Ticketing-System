import uuid
from datetime import datetime

from pydantic import BaseModel


class VoucherBulkCreate(BaseModel):
    ticket_type_id: uuid.UUID
    prefix: str = "POT26"
    count: int = 10


class VoucherClaimRequest(BaseModel):
    code: str
    name: str
    email: str
    company: str | None = None
    title: str | None = None


class VoucherOut(BaseModel):
    id: uuid.UUID
    code: str
    ticket_type_id: uuid.UUID
    is_used: bool
    used_by_email: str | None
    used_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
