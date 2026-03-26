"""Email service using SendGrid. Falls back to logging when SENDGRID_API_KEY is not set."""
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

SENDGRID_API = "https://api.sendgrid.com/v3/mail/send"


async def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """Send an email via SendGrid. Returns True on success."""
    if not settings.sendgrid_api_key:
        logger.info(f"[EMAIL STUB] To: {to_email} | Subject: {subject}")
        logger.info(f"[EMAIL STUB] Body: {html_content[:200]}...")
        return True  # succeed silently in dev

    payload = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": settings.from_email, "name": "Proof of Talk 2026"},
        "subject": subject,
        "content": [{"type": "text/html", "value": html_content}],
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(
            SENDGRID_API,
            json=payload,
            headers={
                "Authorization": f"Bearer {settings.sendgrid_api_key}",
                "Content-Type": "application/json",
            },
        )
        if res.status_code >= 400:
            logger.error(f"SendGrid error {res.status_code}: {res.text}")
            return False
        return True


async def send_order_confirmation(to_email: str, order_number: str, total_eur: int, is_complimentary: bool):
    total_display = "Complimentary" if is_complimentary else f"\u20AC{total_eur / 100:.2f}"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h1 style="color: #e8742a;">Proof of Talk 2026</h1>
        <h2>Order Confirmed</h2>
        <p>Thank you for your order!</p>
        <table style="width: 100%; border-collapse: collapse;">
            <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Order Number</strong></td><td style="padding: 8px; border-bottom: 1px solid #eee;">{order_number}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Total</strong></td><td style="padding: 8px; border-bottom: 1px solid #eee;">{total_display}</td></tr>
        </table>
        <p style="margin-top: 20px;">See you at Proof of Talk 2026!</p>
    </div>
    """
    await send_email(to_email, f"Order Confirmed - {order_number}", html)


async def send_application_received(to_email: str, name: str, ticket_type_name: str):
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h1 style="color: #e8742a;">Proof of Talk 2026</h1>
        <h2>Application Received</h2>
        <p>Hi {name},</p>
        <p>We've received your application for the <strong>{ticket_type_name}</strong>. Our team will review it and get back to you shortly.</p>
        <p>Thank you for your interest in Proof of Talk 2026!</p>
    </div>
    """
    await send_email(to_email, f"Application Received - {ticket_type_name}", html)


async def send_application_approved(
    to_email: str, name: str, ticket_type_name: str, voucher_code: str | None, is_complimentary: bool
):
    if is_complimentary and voucher_code:
        action = f"""
        <p>Use the following code to claim your pass:</p>
        <div style="background: #f5f5f5; padding: 16px; border-radius: 8px; text-align: center; margin: 16px 0;">
            <span style="font-size: 24px; font-family: monospace; font-weight: bold; color: #e8742a;">{voucher_code}</span>
        </div>
        <p>Visit <a href="{settings.frontend_url}">our ticket page</a> to claim your pass.</p>
        """
    else:
        action = f"""
        <p>You can now purchase your <strong>{ticket_type_name}</strong> at <a href="{settings.frontend_url}">our ticket page</a>.</p>
        """

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h1 style="color: #e8742a;">Proof of Talk 2026</h1>
        <h2>Application Approved!</h2>
        <p>Hi {name},</p>
        <p>Great news! Your application for the <strong>{ticket_type_name}</strong> has been approved.</p>
        {action}
        <p>See you at Proof of Talk 2026!</p>
    </div>
    """
    await send_email(to_email, f"Application Approved - {ticket_type_name}", html)


async def send_application_rejected(to_email: str, name: str, ticket_type_name: str, reason: str | None):
    reason_text = f"<p><strong>Reason:</strong> {reason}</p>" if reason else ""
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h1 style="color: #e8742a;">Proof of Talk 2026</h1>
        <h2>Application Update</h2>
        <p>Hi {name},</p>
        <p>Thank you for your interest in the <strong>{ticket_type_name}</strong>. Unfortunately, we're unable to approve your application at this time.</p>
        {reason_text}
        <p>You may still purchase other ticket types at <a href="{settings.frontend_url}">our ticket page</a>.</p>
    </div>
    """
    await send_email(to_email, f"Application Update - {ticket_type_name}", html)


async def send_custom_email(to_email: str, subject: str, body: str):
    """Admin sends a custom email from the dashboard."""
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h1 style="color: #e8742a;">Proof of Talk 2026</h1>
        {body}
    </div>
    """
    return await send_email(to_email, subject, html)
