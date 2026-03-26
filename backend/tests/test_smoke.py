"""Phase 1 smoke tests — validate core ticket purchase flow, admin, vouchers, CSV export."""

import pytest


@pytest.mark.asyncio
async def test_health(client):
    res = await client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_list_ticket_types(client, seed_data):
    res = await client.get("/api/tickets/types")
    assert res.status_code == 200
    types = res.json()
    assert len(types) >= 2
    names = [t["name"] for t in types]
    assert "General Pass" in names
    assert "Speaker Pass" in names


@pytest.mark.asyncio
async def test_create_order_paid(client, seed_data):
    general_id = str(seed_data["general"].id)
    res = await client.post(
        "/api/orders",
        json={
            "attendee": {"email": "buyer@test.com", "name": "Test Buyer", "company": "TestCo"},
            "items": [{"ticket_type_id": general_id, "quantity": 1}],
        },
    )
    assert res.status_code == 201
    order = res.json()
    assert order["order_number"].startswith("POT-")
    assert order["total_eur"] == 119900
    assert order["payment_status"] == "unpaid"
    assert order["status"] == "pending"
    assert order["attendee"]["email"] == "buyer@test.com"


@pytest.mark.asyncio
async def test_create_order_complimentary(client, seed_data):
    speaker_id = str(seed_data["speaker"].id)
    res = await client.post(
        "/api/orders",
        json={
            "attendee": {"email": "speaker@test.com", "name": "Test Speaker"},
            "items": [{"ticket_type_id": speaker_id, "quantity": 1}],
        },
    )
    assert res.status_code == 201
    order = res.json()
    assert order["total_eur"] == 0
    assert order["payment_status"] == "complimentary"
    assert order["status"] == "confirmed"


@pytest.mark.asyncio
async def test_get_order(client, seed_data):
    # Create an order first
    general_id = str(seed_data["general"].id)
    create_res = await client.post(
        "/api/orders",
        json={
            "attendee": {"email": "lookup@test.com", "name": "Lookup User"},
            "items": [{"ticket_type_id": general_id, "quantity": 1}],
        },
    )
    order_id = create_res.json()["id"]
    res = await client.get(f"/api/orders/{order_id}")
    assert res.status_code == 200
    assert res.json()["id"] == order_id


@pytest.mark.asyncio
async def test_admin_login(client, seed_data):
    res = await client.post(
        "/api/auth/login",
        json={"email": "test@admin.com", "password": "testpass"},
    )
    assert res.status_code == 200
    assert "access_token" in res.json()


@pytest.mark.asyncio
async def test_admin_login_wrong_password(client, seed_data):
    res = await client.post(
        "/api/auth/login",
        json={"email": "test@admin.com", "password": "wrong"},
    )
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_admin_list_orders(client, seed_data):
    # Login
    login_res = await client.post(
        "/api/auth/login",
        json={"email": "test@admin.com", "password": "testpass"},
    )
    token = login_res.json()["access_token"]

    res = await client.get("/api/orders", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)


@pytest.mark.asyncio
async def test_admin_list_orders_unauthorized(client):
    res = await client.get("/api/orders")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_admin_filter_orders_by_name(client, seed_data):
    # Create a test order
    general_id = str(seed_data["general"].id)
    await client.post(
        "/api/orders",
        json={
            "attendee": {"email": "filter@test.com", "name": "Filterable Person"},
            "items": [{"ticket_type_id": general_id, "quantity": 1}],
        },
    )

    login_res = await client.post(
        "/api/auth/login",
        json={"email": "test@admin.com", "password": "testpass"},
    )
    token = login_res.json()["access_token"]

    res = await client.get(
        "/api/orders?name=Filterable",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    orders = res.json()
    assert all("Filterable" in o["attendee"]["name"] for o in orders)


@pytest.mark.asyncio
async def test_csv_export(client, seed_data):
    login_res = await client.post(
        "/api/auth/login",
        json={"email": "test@admin.com", "password": "testpass"},
    )
    token = login_res.json()["access_token"]

    res = await client.get(
        "/api/orders/export/csv",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert "text/csv" in res.headers.get("content-type", "")
    content = res.text
    assert "Order Number" in content


@pytest.mark.asyncio
async def test_voucher_bulk_create(client, seed_data):
    login_res = await client.post(
        "/api/auth/login",
        json={"email": "test@admin.com", "password": "testpass"},
    )
    token = login_res.json()["access_token"]

    speaker_id = str(seed_data["speaker"].id)
    res = await client.post(
        "/api/vouchers/bulk",
        json={"ticket_type_id": speaker_id, "prefix": "TESTV", "count": 5},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    vouchers = res.json()
    assert len(vouchers) == 5
    assert all(v["code"].startswith("TESTV-") for v in vouchers)


@pytest.mark.asyncio
async def test_voucher_validate_and_claim(client, seed_data):
    login_res = await client.post(
        "/api/auth/login",
        json={"email": "test@admin.com", "password": "testpass"},
    )
    token = login_res.json()["access_token"]

    speaker_id = str(seed_data["speaker"].id)
    voucher_res = await client.post(
        "/api/vouchers/bulk",
        json={"ticket_type_id": speaker_id, "prefix": "CLAIM", "count": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    code = voucher_res.json()[0]["code"]

    # Validate
    val_res = await client.get(f"/api/vouchers/validate/{code}")
    assert val_res.status_code == 200
    assert val_res.json()["valid"] is True

    # Claim via order
    order_res = await client.post(
        "/api/orders",
        json={
            "attendee": {"email": "claimer@test.com", "name": "Voucher Claimer"},
            "items": [{"ticket_type_id": speaker_id, "quantity": 1}],
            "voucher_code": code,
        },
    )
    assert order_res.status_code == 201
    assert order_res.json()["payment_status"] == "complimentary"

    # Voucher should now be invalid
    val_res2 = await client.get(f"/api/vouchers/validate/{code}")
    assert val_res2.status_code == 400


@pytest.mark.asyncio
async def test_invalid_voucher_rejected(client, seed_data):
    speaker_id = str(seed_data["speaker"].id)
    res = await client.post(
        "/api/orders",
        json={
            "attendee": {"email": "bad@test.com", "name": "Bad Voucher"},
            "items": [{"ticket_type_id": speaker_id, "quantity": 1}],
            "voucher_code": "FAKE-CODE-123",
        },
    )
    assert res.status_code == 400
    assert "Invalid" in res.json()["detail"]
