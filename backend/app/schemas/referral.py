import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class ReferralCreate(BaseModel):
    owner_name: str
    owner_email: EmailStr
    code: str | None = None  # auto-generated if not provided


class ReferralOut(BaseModel):
    id: uuid.UUID
    code: str
    owner_name: str
    owner_email: str
    clicks: int
    orders_count: int
    revenue_eur: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ReferralStatsOut(BaseModel):
    id: uuid.UUID
    code: str
    owner_name: str
    owner_email: str
    clicks: int
    orders_count: int
    revenue_eur: int
    conversion_rate: float  # orders / clicks


class ReferralLeaderboard(BaseModel):
    entries: list[ReferralStatsOut]
