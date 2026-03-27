import uuid
from datetime import datetime

from pydantic import BaseModel


class CheckInRequest(BaseModel):
    order_id: uuid.UUID
    device_id: str | None = None
    notes: str | None = None


class CheckInBatchRequest(BaseModel):
    """For syncing offline check-ins."""
    entries: list["OfflineCheckIn"]


class OfflineCheckIn(BaseModel):
    order_id: uuid.UUID
    device_id: str
    checked_in_at: datetime
    notes: str | None = None


class CheckInOut(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    order_number: str
    attendee_name: str
    attendee_email: str
    ticket_type: str
    checked_in_by: str | None
    device_id: str | None
    notes: str | None
    checked_in_at: datetime

    model_config = {"from_attributes": True}


class CheckInStats(BaseModel):
    total_confirmed: int
    total_checked_in: int
    check_in_rate: float
