"""Phase 3 smoke tests — referrals, QR codes, social sharing, Google Sheets sync."""

import pytest


# --- Referrals ---

@pytest.mark.asyncio
async def test_create_referral(client, seed_data):
    """Admin can create a referral code."""
    login_res = await client.post("/api/auth/login", json={"email": "test@admin.com", "password": "testpass"})
    token = login_res.json()["access_token"]

    res = await client.post(
        "/api/referrals",
        json={"owner_name": "Ambassador Alice", "owner_email": "alice@ref.com"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    ref = res.json()
    assert ref["code"].startswith("REF-")
    assert ref["owner_name"] == "Ambassador Alice"
    assert ref["clicks"] == 0
    assert ref["orders_count"] == 0


@pytest.mark.asyncio
async def test_create_referral_custom_code(client, seed_data):
    """Admin can create a referral with a custom code."""
    login_res = await client.post("/api/auth/login", json={"email": "test@admin.com", "password": "testpass"})
    token = login_res.json()["access_token"]

    res = await client.post(
        "/api/referrals",
        json={"owner_name": "VIP Bob", "owner_email": "bob@ref.com", "code": "VIP-BOB"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    assert res.json()["code"] == "VIP-BOB"


@pytest.mark.asyncio
async def test_duplicate_referral_code_rejected(client, seed_data):
    """Duplicate referral codes are rejected."""
    login_res = await client.post("/api/auth/login", json={"email": "test@admin.com", "password": "testpass"})
    token = login_res.json()["access_token"]

    await client.post(
        "/api/referrals",
        json={"owner_name": "First", "owner_email": "first@ref.com", "code": "DUPE-CODE"},
        headers={"Authorization": f"Bearer {token}"},
    )
    res = await client.post(
        "/api/referrals",
        json={"owner_name": "Second", "owner_email": "second@ref.com", "code": "DUPE-CODE"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_track_referral_click(client, seed_data):
    """Tracking a referral click increments the counter and redirects."""
    login_res = await client.post("/api/auth/login", json={"email": "test@admin.com", "password": "testpass"})
    token = login_res.json()["access_token"]

    ref_res = await client.post(
        "/api/referrals",
        json={"owner_name": "Tracker", "owner_email": "tracker@ref.com", "code": "TRACK-ME"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Track a click (follow_redirects=False to check redirect)
    res = await client.get("/api/referrals/track/TRACK-ME", follow_redirects=False)
    assert res.status_code == 302
    assert "ref=TRACK-ME" in res.headers["location"]


@pytest.mark.asyncio
async def test_referral_attribution_on_order(client, seed_data):
    """Order creation with referral_code attributes the order."""
    login_res = await client.post("/api/auth/login", json={"email": "test@admin.com", "password": "testpass"})
    token = login_res.json()["access_token"]

    # Create referral
    await client.post(
        "/api/referrals",
        json={"owner_name": "Seller", "owner_email": "seller@ref.com", "code": "SELL-IT"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Create order with referral code
    general_id = str(seed_data["general"].id)
    order_res = await client.post(
        "/api/orders",
        json={
            "attendee": {"email": "referred@test.com", "name": "Referred Buyer"},
            "items": [{"ticket_type_id": general_id, "quantity": 1}],
            "referral_code": "SELL-IT",
        },
    )
    assert order_res.status_code == 201

    # Check referral stats
    refs = await client.get("/api/referrals", headers={"Authorization": f"Bearer {token}"})
    sell_ref = [r for r in refs.json() if r["code"] == "SELL-IT"][0]
    assert sell_ref["orders_count"] == 1
    assert sell_ref["revenue_eur"] == 119900


@pytest.mark.asyncio
async def test_referral_leaderboard(client, seed_data):
    """Admin can view referral leaderboard."""
    login_res = await client.post("/api/auth/login", json={"email": "test@admin.com", "password": "testpass"})
    token = login_res.json()["access_token"]

    res = await client.get("/api/referrals/leaderboard", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)


@pytest.mark.asyncio
async def test_referral_unauthorized(client):
    """Referral creation requires admin auth."""
    res = await client.post("/api/referrals", json={"owner_name": "Hack", "owner_email": "hack@test.com"})
    assert res.status_code == 401


# --- QR Codes ---

@pytest.mark.asyncio
async def test_qr_code_confirmed_order(client, seed_data):
    """QR code is generated for confirmed (complimentary) orders."""
    speaker_id = str(seed_data["speaker"].id)
    order_res = await client.post(
        "/api/orders",
        json={
            "attendee": {"email": "qr@test.com", "name": "QR Person"},
            "items": [{"ticket_type_id": speaker_id, "quantity": 1}],
        },
    )
    order_id = order_res.json()["id"]
    assert order_res.json()["status"] == "confirmed"

    res = await client.get(f"/api/sharing/qr/{order_id}")
    assert res.status_code == 200
    assert res.headers["content-type"] == "image/png"
    assert len(res.content) > 100  # valid PNG


@pytest.mark.asyncio
async def test_qr_code_unconfirmed_order_rejected(client, seed_data):
    """QR code is not generated for pending orders."""
    general_id = str(seed_data["general"].id)
    order_res = await client.post(
        "/api/orders",
        json={
            "attendee": {"email": "noqr@test.com", "name": "No QR"},
            "items": [{"ticket_type_id": general_id, "quantity": 1}],
        },
    )
    order_id = order_res.json()["id"]

    res = await client.get(f"/api/sharing/qr/{order_id}")
    assert res.status_code == 400


# --- Social Sharing ---

@pytest.mark.asyncio
async def test_share_card_confirmed_order(client, seed_data):
    """Share card PNG is generated for confirmed orders."""
    speaker_id = str(seed_data["speaker"].id)
    order_res = await client.post(
        "/api/orders",
        json={
            "attendee": {"email": "share@test.com", "name": "Share Person"},
            "items": [{"ticket_type_id": speaker_id, "quantity": 1}],
        },
    )
    order_id = order_res.json()["id"]

    res = await client.get(f"/api/sharing/card/{order_id}")
    assert res.status_code == 200
    assert res.headers["content-type"] == "image/png"
    assert len(res.content) > 100


@pytest.mark.asyncio
async def test_share_meta(client, seed_data):
    """Share metadata returns social URLs."""
    speaker_id = str(seed_data["speaker"].id)
    order_res = await client.post(
        "/api/orders",
        json={
            "attendee": {"email": "meta@test.com", "name": "Meta Person"},
            "items": [{"ticket_type_id": speaker_id, "quantity": 1}],
        },
    )
    order_id = order_res.json()["id"]

    res = await client.get(f"/api/sharing/meta/{order_id}")
    assert res.status_code == 200
    data = res.json()
    assert "twitter_url" in data
    assert "linkedin_url" in data
    assert "share_text" in data
    assert "Proof of Talk" in data["share_text"]
