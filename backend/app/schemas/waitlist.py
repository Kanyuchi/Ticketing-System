import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class WaitlistJoin(BaseModel):
    ticket_type_id: uuid.UUID
    email: EmailStr
    name: str


class WaitlistOut(BaseModel):
    id: uuid.UUID
    ticket_type_id: uuid.UUID
    ticket_type_name: str
    email: str
    name: str
    position: int
    notified: bool
    created_at: datetime

    model_config = {"from_attributes": True}
