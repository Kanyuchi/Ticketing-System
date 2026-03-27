"""Google Sheets live sync service.

Pushes order data to a configured Google Sheet for real-time sales tracking.
Requires a service account JSON key file.

Falls back to logging when credentials are not configured.
"""
import logging
from datetime import datetime, timezone

import gspread
from google.oauth2.service_account import Credentials

from app.core.config import settings

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

_client = None


def _get_client():
    global _client
    if _client:
        return _client
    if not settings.google_sheets_credentials_file:
        return None
    creds = Credentials.from_service_account_file(
        settings.google_sheets_credentials_file, scopes=SCOPES
    )
    _client = gspread.authorize(creds)
    return _client


def sync_order_to_sheet(
    order_number: str,
    attendee_name: str,
    attendee_email: str,
    ticket_type: str,
    total_eur: int,
    payment_status: str,
    order_status: str,
):
    """Append an order row to the configured Google Sheet."""
    client = _get_client()
    if not client or not settings.google_sheets_id:
        logger.info(
            f"[SHEETS STUB] Order {order_number}: {attendee_name} | {ticket_type} | "
            f"\u20AC{total_eur / 100:.2f} | {payment_status}"
        )
        return

    try:
        sheet = client.open_by_key(settings.google_sheets_id).sheet1

        # Ensure header row exists
        existing = sheet.get_all_values()
        if not existing:
            sheet.append_row([
                "Order Number", "Name", "Email", "Ticket Type",
                "Total (EUR)", "Payment Status", "Order Status", "Timestamp",
            ])

        sheet.append_row([
            order_number,
            attendee_name,
            attendee_email,
            ticket_type,
            f"{total_eur / 100:.2f}",
            payment_status,
            order_status,
            datetime.now(timezone.utc).isoformat(),
        ])
        logger.info(f"Synced order {order_number} to Google Sheets")
    except Exception as e:
        logger.error(f"Google Sheets sync failed for {order_number}: {e}")


def sync_summary_to_sheet(sales_by_type: dict[str, dict]):
    """Update a summary tab with sales aggregates."""
    client = _get_client()
    if not client or not settings.google_sheets_id:
        logger.info(f"[SHEETS STUB] Summary sync: {sales_by_type}")
        return

    try:
        spreadsheet = client.open_by_key(settings.google_sheets_id)
        try:
            summary = spreadsheet.worksheet("Summary")
        except gspread.exceptions.WorksheetNotFound:
            summary = spreadsheet.add_worksheet(title="Summary", rows=20, cols=5)

        summary.clear()
        summary.append_row(["Ticket Type", "Sold", "Revenue (EUR)", "Last Updated"])
        for tt_name, data in sales_by_type.items():
            summary.append_row([
                tt_name,
                data["sold"],
                f"{data['revenue'] / 100:.2f}",
                datetime.now(timezone.utc).isoformat(),
            ])
        logger.info("Synced summary to Google Sheets")
    except Exception as e:
        logger.error(f"Google Sheets summary sync failed: {e}")
