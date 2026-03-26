"""Phase 2 smoke tests — applications, email triggers, ticket upgrades."""

import pytest


@pytest.mark.asyncio
async def test_submit_application_press(client, seed_data):
    """Submit a Press pass application."""
    press_id = str(seed_data["press"].id)
    res = await client.post(
        "/api/applications",
        json={
            "ticket_type_id": press_id,
            "name": "Jane Reporter",
            "email": "jane@press.com",
            "company": "TechNews",
            "publication": "TechNews Daily",
            "portfolio_url": "https://technews.com/jane",
            "reason": "I cover blockchain events",
        },
    )
    assert res.status_code == 201
    app = res.json()
    assert app["status"] == "pending"
    assert app["name"] == "Jane Reporter"
    assert app["publication"] == "TechNews Daily"


@pytest.mark.asyncio
async def test_submit_application_startup(client, seed_data):
    """Submit a Startup pass application (needs a startup ticket type)."""
    # First create a startup ticket type via admin
    login_res = await client.post(
        "/api/auth/login",
        json={"email": "test@admin.com", "password": "testpass"},
    )
    token = login_res.json()["access_token"]

    create_res = await client.post(
        "/api/tickets/types",
        json={
            "name": "Startup Pass",
            "category": "startup",
            "price_eur": 99900,
            "requires_application": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    startup_id = create_res.json()["id"]

    res = await client.post(
        "/api/applications",
        json={
            "ticket_type_id": startup_id,
            "name": "Startup Founder",
            "email": "founder@startup.io",
            "startup_name": "CoolStartup",
            "startup_website": "https://coolstartup.io",
            "startup_stage": "seed",
            "reason": "Building in web3",
        },
    )
    assert res.status_code == 201
    assert res.json()["startup_name"] == "CoolStartup"


@pytest.mark.asyncio
async def test_duplicate_application_rejected(client, seed_data):
    """Duplicate application for same email + ticket type is rejected."""
    press_id = str(seed_data["press"].id)
    await client.post(
        "/api/applications",
        json={
            "ticket_type_id": press_id,
            "name": "Duplicate Person",
            "email": "dupe@test.com",
        },
    )
    res = await client.post(
        "/api/applications",
        json={
            "ticket_type_id": press_id,
            "name": "Duplicate Person",
            "email": "dupe@test.com",
        },
    )
    assert res.status_code == 400
    assert "already" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_application_requires_application_type(client, seed_data):
    """Cannot apply for a non-application ticket type."""
    general_id = str(seed_data["general"].id)
    res = await client.post(
        "/api/applications",
        json={
            "ticket_type_id": general_id,
            "name": "Wrong Type",
            "email": "wrong@test.com",
        },
    )
    assert res.status_code == 400
    assert "does not require" in res.json()["detail"]


@pytest.mark.asyncio
async def test_approve_press_application_generates_voucher(client, seed_data):
    """Approving a Press application generates a voucher code."""
    press_id = str(seed_data["press"].id)

    # Submit application
    app_res = await client.post(
        "/api/applications",
        json={
            "ticket_type_id": press_id,
            "name": "Approved Press",
            "email": "approved@press.com",
            "publication": "Big Outlet",
        },
    )
    app_id = app_res.json()["id"]

    # Login as admin
    login_res = await client.post(
        "/api/auth/login",
        json={"email": "test@admin.com", "password": "testpass"},
    )
    token = login_res.json()["access_token"]

    # Approve
    review_res = await client.post(
        f"/api/applications/{app_id}/review",
        json={"status": "approved"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert review_res.status_code == 200
    reviewed = review_res.json()
    assert reviewed["status"] == "approved"
    assert reviewed["voucher_code"] is not None
    assert reviewed["voucher_code"].startswith("APPROVED-")


@pytest.mark.asyncio
async def test_reject_application(client, seed_data):
    """Rejecting an application records the reason."""
    press_id = str(seed_data["press"].id)

    app_res = await client.post(
        "/api/applications",
        json={
            "ticket_type_id": press_id,
            "name": "Rejected Person",
            "email": "rejected@test.com",
        },
    )
    app_id = app_res.json()["id"]

    login_res = await client.post(
        "/api/auth/login",
        json={"email": "test@admin.com", "password": "testpass"},
    )
    token = login_res.json()["access_token"]

    review_res = await client.post(
        f"/api/applications/{app_id}/review",
        json={"status": "rejected", "rejection_reason": "Not eligible"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert review_res.status_code == 200
    assert review_res.json()["status"] == "rejected"
    assert review_res.json()["rejection_reason"] == "Not eligible"


@pytest.mark.asyncio
async def test_cannot_review_twice(client, seed_data):
    """Cannot review an already-reviewed application."""
    press_id = str(seed_data["press"].id)

    app_res = await client.post(
        "/api/applications",
        json={
            "ticket_type_id": press_id,
            "name": "Double Review",
            "email": "double@test.com",
        },
    )
    app_id = app_res.json()["id"]

    login_res = await client.post(
        "/api/auth/login",
        json={"email": "test@admin.com", "password": "testpass"},
    )
    token = login_res.json()["access_token"]

    await client.post(
        f"/api/applications/{app_id}/review",
        json={"status": "approved"},
        headers={"Authorization": f"Bearer {token}"},
    )
    res = await client.post(
        f"/api/applications/{app_id}/review",
        json={"status": "rejected"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400
    assert "already" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_applications_admin(client, seed_data):
    """Admin can list applications with status filter."""
    login_res = await client.post(
        "/api/auth/login",
        json={"email": "test@admin.com", "password": "testpass"},
    )
    token = login_res.json()["access_token"]

    res = await client.get(
        "/api/applications",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert isinstance(res.json(), list)


@pytest.mark.asyncio
async def test_list_applications_unauthorized(client):
    """Applications listing requires admin auth."""
    res = await client.get("/api/applications")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_get_application_status(client, seed_data):
    """Public can check their application status."""
    press_id = str(seed_data["press"].id)
    app_res = await client.post(
        "/api/applications",
        json={
            "ticket_type_id": press_id,
            "name": "Status Check",
            "email": "status@test.com",
        },
    )
    app_id = app_res.json()["id"]

    res = await client.get(f"/api/applications/{app_id}")
    assert res.status_code == 200
    assert res.json()["status"] == "pending"


@pytest.mark.asyncio
async def test_send_email_admin(client, seed_data):
    """Admin can send a custom email."""
    login_res = await client.post(
        "/api/auth/login",
        json={"email": "test@admin.com", "password": "testpass"},
    )
    token = login_res.json()["access_token"]

    res = await client.post(
        "/api/emails/send",
        json={
            "to_email": "attendee@test.com",
            "subject": "Test Email",
            "body": "<p>Hello from admin!</p>",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert res.json()["sent"] is True


@pytest.mark.asyncio
async def test_send_email_unauthorized(client):
    """Email sending requires admin auth."""
    res = await client.post(
        "/api/emails/send",
        json={
            "to_email": "test@test.com",
            "subject": "Hack",
            "body": "nope",
        },
    )
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_upgrade_calculate(client, seed_data):
    """Calculate upgrade price difference."""
    general_id = str(seed_data["general"].id)

    # Create a VIP ticket type for upgrade target
    login_res = await client.post(
        "/api/auth/login",
        json={"email": "test@admin.com", "password": "testpass"},
    )
    token = login_res.json()["access_token"]

    vip_res = await client.post(
        "/api/tickets/types",
        json={"name": "VIP Pass", "category": "vip", "price_eur": 249900},
        headers={"Authorization": f"Bearer {token}"},
    )
    vip_id = vip_res.json()["id"]

    # Create an order for General pass
    order_res = await client.post(
        "/api/orders",
        json={
            "attendee": {"email": "upgrader@test.com", "name": "Upgrader"},
            "items": [{"ticket_type_id": general_id, "quantity": 1}],
        },
    )
    order_id = order_res.json()["id"]

    # Calculate upgrade
    calc_res = await client.post(
        "/api/upgrades/calculate",
        json={"order_id": order_id, "new_ticket_type_id": vip_id},
    )
    assert calc_res.status_code == 200
    calc = calc_res.json()
    assert calc["price_difference"] == 249900 - 119900  # VIP - General
    assert calc["current_ticket"] == "General Pass"
    assert calc["new_ticket"] == "VIP Pass"


@pytest.mark.asyncio
async def test_upgrade_cannot_downgrade(client, seed_data):
    """Cannot 'upgrade' to a cheaper ticket."""
    general_id = str(seed_data["general"].id)
    press_id = str(seed_data["press"].id)

    order_res = await client.post(
        "/api/orders",
        json={
            "attendee": {"email": "downgrader@test.com", "name": "Downgrader"},
            "items": [{"ticket_type_id": general_id, "quantity": 1}],
        },
    )
    order_id = order_res.json()["id"]

    calc_res = await client.post(
        "/api/upgrades/calculate",
        json={"order_id": order_id, "new_ticket_type_id": press_id},
    )
    assert calc_res.status_code == 400
    detail = calc_res.json()["detail"].lower()
    assert "higher" in detail or "application" in detail
