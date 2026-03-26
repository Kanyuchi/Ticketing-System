import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class AttendeeCreate(BaseModel):
    email: EmailStr
    name: str
    company: str | None = None
    title: str | None = None


class AttendeeOut(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    company: str | None
    title: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
