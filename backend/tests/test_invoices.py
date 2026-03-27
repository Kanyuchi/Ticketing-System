"""Invoice generation tests."""

import pytest


async def _admin_token(client):
    res = await client.post("/api/auth/login", json={"email": "test@admin.com", "password": "testpass"})
    return res.json()["access_token"]


@pytest.mark.asyncio
async def test_invoice_confirmed_order(client, seed_data):
    """Invoice PDF is generated for confirmed (complimentary) orders."""
    speaker_id = str(seed_data["speaker"].id)
    order_res = await client.post(
        "/api/orders",
        json={
            "attendee": {"email": "invoice@test.com", "name": "Invoice Person", "company": "Test Corp"},
            "items": [{"ticket_type_id": speaker_id, "quantity": 1}],
        },
    )
    assert order_res.json()["status"] == "confirmed"
    order_id = order_res.json()["id"]

    res = await client.get(f"/api/orders/{order_id}/invoice")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    # Valid PDF starts with %PDF
    assert res.content[:5] == b"%PDF-"
    assert len(res.content) > 500  # meaningful PDF


@pytest.mark.asyncio
async def test_invoice_pending_order_rejected(client, seed_data):
    """Invoice is not generated for pending/unpaid orders."""
    general_id = str(seed_data["general"].id)
    order_res = await client.post(
        "/api/orders",
        json={
            "attendee": {"email": "noinvoice@test.com", "name": "No Invoice"},
            "items": [{"ticket_type_id": general_id, "quantity": 1}],
        },
    )
    assert order_res.json()["status"] == "pending"
    order_id = order_res.json()["id"]

    res = await client.get(f"/api/orders/{order_id}/invoice")
    assert res.status_code == 400
    assert "confirmed" in res.json()["detail"]


@pytest.mark.asyncio
async def test_invoice_nonexistent_order(client, seed_data):
    """Invoice for non-existent order returns 400."""
    res = await client.get("/api/orders/00000000-0000-0000-0000-000000000000/invoice")
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_invoice_with_voucher_order(client, seed_data):
    """Invoice is generated for a confirmed order that used a voucher."""
    token = await _admin_token(client)

    # Generate a voucher for speaker pass
    speaker_id = str(seed_data["speaker"].id)
    voucher_res = await client.post(
        "/api/vouchers/bulk",
        json={"ticket_type_id": speaker_id, "prefix": "INV-TEST", "count": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    code = voucher_res.json()[0]["code"]

    # Create order with voucher
    order_res = await client.post(
        "/api/orders",
        json={
            "attendee": {"email": "voucher-inv@test.com", "name": "Voucher Invoice"},
            "items": [{"ticket_type_id": speaker_id, "quantity": 1}],
            "voucher_code": code,
        },
    )
    assert order_res.json()["status"] == "confirmed"

    res = await client.get(f"/api/orders/{order_res.json()['id']}/invoice")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
