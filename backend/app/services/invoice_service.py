"""PDF invoice generation for Proof of Talk 2026.

Generates branded invoices with order details, line items, and VAT info.
"""
import io
import uuid
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.ticket_type import TicketType

# Branding
COMPANY_NAME = "Proof of Talk 2026"
COMPANY_ADDRESS = "Proof of Talk GmbH\nBerlin, Germany"
COMPANY_EMAIL = "tickets@proofoftalk.io"
COMPANY_VAT = "DE000000000"  # Placeholder — replace with real VAT number
CURRENCY = "EUR"

# Colors
BRAND_DARK = colors.HexColor("#1a1a1a")
BRAND_ORANGE = colors.HexColor("#e8642c")
BRAND_GRAY = colors.HexColor("#666666")
BRAND_LIGHT_GRAY = colors.HexColor("#f5f5f5")


def _format_eur(cents: int) -> str:
    """Format cents as EUR string."""
    return f"\u20AC{cents / 100:,.2f}"


async def generate_invoice_pdf(db: AsyncSession, order_id: uuid.UUID) -> bytes:
    """Generate a branded PDF invoice for an order. Returns PDF bytes."""
    # Fetch order with relationships
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.attendee), selectinload(Order.items))
    )
    order = result.scalar_one_or_none()
    if not order:
        raise ValueError("Order not found")

    if order.status != OrderStatus.CONFIRMED:
        raise ValueError("Invoice can only be generated for confirmed orders")

    # Fetch ticket type names for each item
    line_items = []
    for item in order.items:
        tt_result = await db.execute(select(TicketType).where(TicketType.id == item.ticket_type_id))
        tt = tt_result.scalar_one_or_none()
        line_items.append({
            "name": tt.name if tt else "Unknown Ticket",
            "quantity": item.quantity,
            "unit_price": item.unit_price_eur,
            "total": item.unit_price_eur * item.quantity,
        })

    # Build PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "InvoiceTitle",
        parent=styles["Title"],
        fontSize=28,
        textColor=BRAND_DARK,
        spaceAfter=4 * mm,
        fontName="Helvetica-Bold",
    )
    heading_style = ParagraphStyle(
        "InvoiceHeading",
        parent=styles["Heading2"],
        fontSize=11,
        textColor=BRAND_ORANGE,
        spaceBefore=6 * mm,
        spaceAfter=2 * mm,
        fontName="Helvetica-Bold",
    )
    normal_style = ParagraphStyle(
        "InvoiceNormal",
        parent=styles["Normal"],
        fontSize=10,
        textColor=BRAND_DARK,
        leading=14,
    )
    small_style = ParagraphStyle(
        "InvoiceSmall",
        parent=styles["Normal"],
        fontSize=8,
        textColor=BRAND_GRAY,
        leading=11,
    )

    elements = []

    # --- Header ---
    elements.append(Paragraph(COMPANY_NAME, title_style))
    elements.append(Paragraph("INVOICE", ParagraphStyle(
        "InvoiceLabel",
        parent=styles["Normal"],
        fontSize=12,
        textColor=BRAND_ORANGE,
        fontName="Helvetica-Bold",
    )))
    elements.append(Spacer(1, 6 * mm))

    # --- Invoice meta + addresses (side by side) ---
    invoice_date = order.updated_at or order.created_at
    meta_data = [
        ["Invoice Number:", f"INV-{order.order_number}"],
        ["Invoice Date:", invoice_date.strftime("%d %B %Y")],
        ["Order Number:", order.order_number],
        ["Payment Status:", order.payment_status.value.title()],
    ]
    meta_table = Table(meta_data, colWidths=[35 * mm, 60 * mm])
    meta_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, -1), BRAND_GRAY),
        ("TEXTCOLOR", (1, 0), (1, -1), BRAND_DARK),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))

    # Bill to
    bill_to_lines = [order.attendee.name]
    if order.attendee.company:
        bill_to_lines.append(order.attendee.company)
    if order.attendee.title:
        bill_to_lines.append(order.attendee.title)
    bill_to_lines.append(order.attendee.email)

    bill_to_text = "<br/>".join(bill_to_lines)

    address_data = [[meta_table, ""]]
    address_table = Table(address_data, colWidths=[100 * mm, 70 * mm])
    address_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(address_table)
    elements.append(Spacer(1, 4 * mm))

    # Bill To section
    elements.append(Paragraph("Bill To", heading_style))
    elements.append(Paragraph(bill_to_text, normal_style))
    elements.append(Spacer(1, 6 * mm))

    # --- Line Items Table ---
    elements.append(Paragraph("Items", heading_style))

    table_data = [["Description", "Qty", "Unit Price", "Total"]]
    for item in line_items:
        table_data.append([
            item["name"],
            str(item["quantity"]),
            _format_eur(item["unit_price"]),
            _format_eur(item["total"]),
        ])

    # Subtotal / Total
    subtotal = sum(item["total"] for item in line_items)
    table_data.append(["", "", "Subtotal:", _format_eur(subtotal)])

    # VAT line (0% for now — event tickets often VAT-exempt or reverse-charge)
    vat_amount = 0
    table_data.append(["", "", "VAT (0%):", _format_eur(vat_amount)])
    table_data.append(["", "", "Total:", _format_eur(subtotal + vat_amount)])

    col_widths = [85 * mm, 15 * mm, 35 * mm, 35 * mm]
    items_table = Table(table_data, colWidths=col_widths)

    num_items = len(line_items)
    items_table.setStyle(TableStyle([
        # Header row
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),

        # Data rows
        ("FONTNAME", (0, 1), (-1, num_items), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, num_items), 9),
        ("BOTTOMPADDING", (0, 1), (-1, num_items), 6),
        ("TOPPADDING", (0, 1), (-1, num_items), 6),
        ("BACKGROUND", (0, 1), (-1, num_items), BRAND_LIGHT_GRAY),

        # Alignment
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),

        # Summary rows
        ("FONTNAME", (2, num_items + 1), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (2, num_items + 1), (-1, -1), 9),
        ("TEXTCOLOR", (2, num_items + 1), (2, -1), BRAND_GRAY),

        # Total row bold
        ("FONTNAME", (2, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (-1, -1), (-1, -1), 11),
        ("TEXTCOLOR", (-1, -1), (-1, -1), BRAND_ORANGE),

        # Grid
        ("LINEBELOW", (0, 0), (-1, 0), 1, BRAND_DARK),
        ("LINEBELOW", (0, num_items), (-1, num_items), 0.5, BRAND_GRAY),
        ("LINEBELOW", (2, -2), (-1, -2), 0.5, colors.HexColor("#dddddd")),

        # Padding
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(items_table)
    elements.append(Spacer(1, 10 * mm))

    # --- Voucher note ---
    if order.voucher_code:
        elements.append(Paragraph(
            f"Voucher applied: <b>{order.voucher_code}</b>",
            small_style,
        ))
        elements.append(Spacer(1, 4 * mm))

    # --- Footer ---
    elements.append(Spacer(1, 10 * mm))
    footer_text = (
        f"{COMPANY_ADDRESS}<br/>"
        f"Email: {COMPANY_EMAIL}<br/>"
        f"VAT: {COMPANY_VAT}<br/><br/>"
        "Thank you for your purchase. This invoice serves as your receipt."
    )
    elements.append(Paragraph(footer_text, small_style))

    # Build
    doc.build(elements)
    return buffer.getvalue()
