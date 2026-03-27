"""Phase 4 smoke tests — check-in, analytics, waitlist, referral rewards, deploy."""

import pytest


# --- Helper: create a confirmed (complimentary) order ---

async def _create_confirmed_order(client, seed_data, email="checkin@test.com", name="Check In Person"):
    speaker_id = str(seed_data["speaker"].id)
    res = await client.post(
        "/api/orders",
        json={
            "attendee": {"email": email, "name": name},
            "items": [{"ticket_type_id": speaker_id, "quantity": 1}],
        },
    )
    assert res.status_code == 201
    assert res.json()["status"] == "confirmed"
    return res.json()


async def _admin_token(client):
    res = await client.post("/api/auth/login", json={"email": "test@admin.com", "password": "testpass"})
    return res.json()["access_token"]


# --- Check-in ---

@pytest.mark.asyncio
async def test_checkin_confirmed_order(client, seed_data):
    """Admin can check in a confirmed order."""
    token = await _admin_token(client)
    order = await _create_confirmed_order(client, seed_data)

    res = await client.post(
        "/api/checkin",
        json={"order_id": order["id"]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["order_id"] == order["id"]
    assert data["attendee_name"] == "Check In Person"
    assert data["checked_in_by"] == "test@admin.com"


@pytest.mark.asyncio
async def test_checkin_duplicate_rejected(client, seed_data):
    """Cannot check in the same order twice."""
    token = await _admin_token(client)
    order = await _create_confirmed_order(client, seed_data, email="dup@test.com")

    await client.post(
        "/api/checkin",
        json={"order_id": order["id"]},
        headers={"Authorization": f"Bearer {token}"},
    )
    res = await client.post(
        "/api/checkin",
        json={"order_id": order["id"]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400
    assert "Already checked in" in res.json()["detail"]


@pytest.mark.asyncio
async def test_checkin_pending_order_rejected(client, seed_data):
    """Cannot check in a pending (unpaid) order."""
    token = await _admin_token(client)
    general_id = str(seed_data["general"].id)

    order_res = await client.post(
        "/api/orders",
        json={
            "attendee": {"email": "pending@test.com", "name": "Pending Person"},
            "items": [{"ticket_type_id": general_id, "quantity": 1}],
        },
    )
    assert order_res.json()["status"] == "pending"

    res = await client.post(
        "/api/checkin",
        json={"order_id": order_res.json()["id"]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400
    assert "not confirmed" in res.json()["detail"]


@pytest.mark.asyncio
async def test_checkin_stats(client, seed_data):
    """Check-in stats reflect confirmed and checked-in counts."""
    token = await _admin_token(client)
    order = await _create_confirmed_order(client, seed_data, email="stats@test.com")

    await client.post(
        "/api/checkin",
        json={"order_id": order["id"]},
        headers={"Authorization": f"Bearer {token}"},
    )

    res = await client.get("/api/checkin/stats", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["total_confirmed"] >= 1
    assert data["total_checked_in"] >= 1
    assert 0.0 < data["check_in_rate"] <= 1.0


@pytest.mark.asyncio
async def test_checkin_verify(client, seed_data):
    """Can verify check-in status by order ID."""
    token = await _admin_token(client)
    order = await _create_confirmed_order(client, seed_data, email="verify@test.com")

    # Not checked in yet
    res = await client.get(
        f"/api/checkin/verify/{order['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.json()["checked_in"] is False

    # Check in
    await client.post(
        "/api/checkin",
        json={"order_id": order["id"]},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Now verified
    res = await client.get(
        f"/api/checkin/verify/{order['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.json()["checked_in"] is True


# --- Analytics ---

@pytest.mark.asyncio
async def test_analytics_dashboard(client, seed_data):
    """Admin can view full analytics dashboard."""
    token = await _admin_token(client)

    # Create a confirmed order to have data
    await _create_confirmed_order(client, seed_data, email="analytics@test.com")

    res = await client.get("/api/analytics/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert "total_revenue_eur" in data
    assert "sales_by_type" in data
    assert "funnel" in data
    assert "top_referrers" in data
    assert len(data["sales_by_type"]) >= 1


@pytest.mark.asyncio
async def test_analytics_sales_by_type(client, seed_data):
    """Sales breakdown shows all ticket types."""
    token = await _admin_token(client)

    res = await client.get("/api/analytics/sales", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    names = [s["ticket_type"] for s in data]
    assert "General Pass" in names


@pytest.mark.asyncio
async def test_analytics_unauthorized(client):
    """Analytics requires admin auth."""
    res = await client.get("/api/analytics/dashboard")
    assert res.status_code == 401


# --- Waitlist ---

@pytest.mark.asyncio
async def test_waitlist_join_sold_out(client, seed_data, db_session):
    """Can join waitlist for a sold-out ticket type."""
    # Make general pass sold out
    general = seed_data["general"]
    general.quantity_total = 1
    general.quantity_sold = 1
    await db_session.commit()

    res = await client.post(
        "/api/waitlist",
        json={
            "ticket_type_id": str(general.id),
            "email": "waiting@test.com",
            "name": "Waiting Person",
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert data["position"] == 1
    assert data["email"] == "waiting@test.com"
    assert data["ticket_type_name"] == "General Pass"


@pytest.mark.asyncio
async def test_waitlist_not_sold_out_rejected(client, seed_data):
    """Cannot join waitlist for available ticket type."""
    res = await client.post(
        "/api/waitlist",
        json={
            "ticket_type_id": str(seed_data["speaker"].id),
            "email": "eager@test.com",
            "name": "Eager Person",
        },
    )
    assert res.status_code == 400
    assert "not sold out" in res.json()["detail"]


@pytest.mark.asyncio
async def test_waitlist_duplicate_rejected(client, seed_data, db_session):
    """Cannot join waitlist twice for same ticket type."""
    general = seed_data["general"]
    general.quantity_total = 1
    general.quantity_sold = 1
    await db_session.commit()

    await client.post(
        "/api/waitlist",
        json={
            "ticket_type_id": str(general.id),
            "email": "dupe-wait@test.com",
            "name": "Dupe Waiter",
        },
    )
    res = await client.post(
        "/api/waitlist",
        json={
            "ticket_type_id": str(general.id),
            "email": "dupe-wait@test.com",
            "name": "Dupe Waiter",
        },
    )
    assert res.status_code == 400
    assert "Already on the waitlist" in res.json()["detail"]


# --- Referral Rewards ---

@pytest.mark.asyncio
async def test_reward_tiers_public(client):
    """Public can view reward tier thresholds."""
    res = await client.get("/api/rewards/tiers")
    assert res.status_code == 200
    tiers = res.json()["tiers"]
    assert len(tiers) == 3
    assert tiers[0]["min_orders"] == 3


@pytest.mark.asyncio
async def test_reward_status_no_tier(client, seed_data):
    """Referral with 0 orders has no tier."""
    token = await _admin_token(client)

    # Create a referral
    await client.post(
        "/api/referrals",
        json={"owner_name": "New Ref", "owner_email": "newref@test.com", "code": "NEW-REF"},
        headers={"Authorization": f"Bearer {token}"},
    )

    res = await client.get("/api/rewards/status?referral_code=NEW-REF")
    assert res.status_code == 200
    data = res.json()
    assert data["current_tier"] is None
    assert data["next_tier"] == "Bronze Ambassador"
    assert data["orders_to_next_tier"] == 3
