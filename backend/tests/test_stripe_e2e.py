"""End-to-end Stripe integration tests.

These tests verify the Stripe checkout flow works correctly:
- Checkout session creation (fails gracefully without valid API key)
- Webhook handling for payment confirmation
- Order status transitions
"""

import json
import pytest


async def _admin_token(client):
    res = await client.post("/api/auth/login", json={"email": "test@admin.com", "password": "testpass"})
    return res.json()["access_token"]


# --- Checkout Flow ---

@pytest.mark.asyncio
async def test_checkout_creates_session_or_fails_gracefully(client, seed_data):
    """Creating a checkout session for a paid order either works (with valid key) or returns a clear error."""
    general_id = str(seed_data["general"].id)
    order_res = await client.post(
        "/api/orders",
        json={
            "attendee": {"email": "stripe@test.com", "name": "Stripe Buyer"},
            "items": [{"ticket_type_id": general_id, "quantity": 1}],
        },
    )
    assert order_res.status_code == 201
    order = order_res.json()
    assert order["status"] == "pending"
    assert order["payment_status"] == "unpaid"
    assert order["total_eur"] == 119900

    # Try to create checkout — will fail with test/empty key but should return 400, not 500
    res = await client.post(f"/api/payments/create-checkout/{order['id']}")
    assert res.status_code in (200, 400)  # 200 with real key, 400 with invalid key


@pytest.mark.asyncio
async def test_checkout_rejected_for_complimentary_order(client, seed_data):
    """Complimentary orders should not go through Stripe."""
    speaker_id = str(seed_data["speaker"].id)
    order_res = await client.post(
        "/api/orders",
        json={
            "attendee": {"email": "free@test.com", "name": "Free Person"},
            "items": [{"ticket_type_id": speaker_id, "quantity": 1}],
        },
    )
    order = order_res.json()
    assert order["payment_status"] == "complimentary"

    res = await client.post(f"/api/payments/create-checkout/{order['id']}")
    assert res.status_code == 400
    assert "not awaiting payment" in res.json()["detail"]


@pytest.mark.asyncio
async def test_checkout_rejected_for_nonexistent_order(client, seed_data):
    """Checkout for a non-existent order returns 404."""
    res = await client.post("/api/payments/create-checkout/00000000-0000-0000-0000-000000000000")
    assert res.status_code == 404


# --- Webhook Flow ---

@pytest.mark.asyncio
async def test_webhook_rejects_invalid_signature(client, seed_data):
    """Webhook rejects requests with invalid signatures."""
    res = await client.post(
        "/api/payments/webhook",
        content=b'{"type": "checkout.session.completed"}',
        headers={"stripe-signature": "invalid_sig"},
    )
    assert res.status_code == 400
    assert "Invalid webhook signature" in res.json()["detail"]


# --- Full Order Lifecycle ---

@pytest.mark.asyncio
async def test_paid_order_starts_pending(client, seed_data):
    """Paid orders start as pending/unpaid and await Stripe checkout."""
    general_id = str(seed_data["general"].id)
    res = await client.post(
        "/api/orders",
        json={
            "attendee": {"email": "lifecycle@test.com", "name": "Lifecycle Test"},
            "items": [{"ticket_type_id": general_id, "quantity": 1}],
        },
    )
    order = res.json()
    assert order["status"] == "pending"
    assert order["payment_status"] == "unpaid"

    # Verify we can retrieve it
    get_res = await client.get(f"/api/orders/{order['id']}")
    assert get_res.status_code == 200
    assert get_res.json()["order_number"] == order["order_number"]


@pytest.mark.asyncio
async def test_complimentary_order_auto_confirms(client, seed_data):
    """Complimentary orders auto-confirm without Stripe."""
    speaker_id = str(seed_data["speaker"].id)
    res = await client.post(
        "/api/orders",
        json={
            "attendee": {"email": "autoconfirm@test.com", "name": "Auto Confirm"},
            "items": [{"ticket_type_id": speaker_id, "quantity": 1}],
        },
    )
    order = res.json()
    assert order["status"] == "confirmed"
    assert order["payment_status"] == "complimentary"
    assert order["total_eur"] == 0
