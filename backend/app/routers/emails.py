from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.admin_user import AdminUser
from app.routers.auth import get_current_admin
from app.services.email_service import send_custom_email

router = APIRouter(prefix="/emails", tags=["emails"])


class SendEmailRequest(BaseModel):
    to_email: EmailStr
    subject: str
    body: str  # HTML body content


@router.post("/send")
async def send_email_from_dashboard(
    data: SendEmailRequest,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: send a custom email to an attendee."""
    success = await send_custom_email(data.to_email, data.subject, data.body)
    return {"sent": success}
