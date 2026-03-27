"""QR code generation for ticket orders."""
import io
import uuid

import qrcode
from qrcode.image.styledpil import StyledPilImage

from app.core.config import settings


def generate_order_qr(order_id: uuid.UUID, order_number: str) -> bytes:
    """Generate a QR code PNG for an order. Encodes a check-in URL."""
    checkin_url = f"{settings.frontend_url}/checkin/{order_id}"

    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=4)
    qr.add_data(checkin_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#2d2d2d", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()


def generate_share_card(name: str, ticket_type_name: str) -> bytes:
    """Generate a simple 'I'm Attending' social share card as PNG."""
    from PIL import Image, ImageDraw, ImageFont

    width, height = 1200, 630
    img = Image.new("RGB", (width, height), "#faf5ef")
    draw = ImageDraw.Draw(img)

    # Use default font (no external fonts needed)
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
        name_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        detail_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
    except (IOError, OSError):
        title_font = ImageFont.load_default()
        name_font = ImageFont.load_default()
        detail_font = ImageFont.load_default()

    # Orange banner at top
    draw.rectangle([(0, 0), (width, 120)], fill="#e8742a")
    draw.text((60, 35), "PROOF OF TALK 2026", fill="white", font=title_font)

    # Main content
    draw.text((60, 180), "I'm Attending!", fill="#1a1a1a", font=title_font)
    draw.text((60, 260), name, fill="#2d2d2d", font=name_font)
    draw.text((60, 320), ticket_type_name, fill="#e8742a", font=name_font)

    # Footer
    draw.rectangle([(0, height - 60), (width, height)], fill="#2d2d2d")
    draw.text((60, height - 45), "proofoftalk.io", fill="white", font=detail_font)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()
