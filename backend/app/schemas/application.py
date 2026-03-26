import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.application import ApplicationStatus


class ApplicationSubmit(BaseModel):
    ticket_type_id: uuid.UUID
    name: str
    email: EmailStr
    company: str | None = None
    title: str | None = None
    reason: str | None = None
    # Press fields
    publication: str | None = None
    portfolio_url: str | None = None
    # Startup fields
    startup_name: str | None = None
    startup_website: str | None = None
    startup_stage: str | None = None


class ApplicationReview(BaseModel):
    status: ApplicationStatus  # approved or rejected
    rejection_reason: str | None = None


class ApplicationOut(BaseModel):
    id: uuid.UUID
    ticket_type_id: uuid.UUID
    status: ApplicationStatus
    name: str
    email: str
    company: str | None
    title: str | None
    reason: str | None
    publication: str | None
    portfolio_url: str | None
    startup_name: str | None
    startup_website: str | None
    startup_stage: str | None
    voucher_code: str | None
    reviewed_by: str | None
    reviewed_at: datetime | None
    rejection_reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
