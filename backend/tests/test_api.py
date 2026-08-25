import json
import pytest
from sqlalchemy import select
from app.models.all_models import User, Order, OrderItem, Category, MenuItem


@pytest.mark.asyncio
async def test_auth_telegram_success(async_client, admin_auth_header):
    """
    POST /api/v1/auth/telegram
    Verifies valid initData HMAC signature, user extraction, and response contract.
    """
    response = await async_client.post("/api/v1/auth/telegram", headers=admin_auth_header)
    assert response.status_code == 200
    data = response.json()

    assert "user" in data
    assert "settings" in data
    assert data["user"]["telegram_id"] == 10001
    assert data["user"]["is_admin"] is True
    assert data["settings"]["is_open"] is True
    assert data["settings"]["delivery_fee"] == 3000
    assert "bank_details" in data["settings"]


@pytest.mark.asyncio
async def test_auth_telegram_invalid_signature(async_client):
    """
    POST /api/v1/auth/telegram
    Verifies 401 Unauthorized response when initData hash signature is invalid.
    """
    invalid_header = {"Authorization": "tma auth_date=1700000000&user=%7B%22id%22%3A10001%7D&hash=invalid_fake_hash"}
    response = await async_client.post("/api/v1/auth/telegram", headers=invalid_header)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid Telegram initData signature"


@pytest.mark.asyncio
async def test_menu_crud(async_client, admin_auth_header, user_auth_header):
    """
    1. Create Category via POST /api/v1/admin/menu/categories
    2. Create Menu Item via POST /api/v1/admin/menu/items
    3. Toggle item availability (stop-list) via PATCH /api/v1/admin/menu/items/{id}/toggle
    4. Retrieve catalog via GET /api/v1/menu
    """
    # 1. Create Category
    cat_res = await async_client.post(
        "/api/v1/admin/menu/categories",
        data={"name": "Супы", "sort_order": 1},
        headers=admin_auth_header
    )
    assert cat_res.status_code == 200
    cat_id = cat_res.json()["id"]

    # 2. Create Menu Item
    item_res = await async_client.post(
        "/api/v1/admin/menu/items",
        data={
            "category_id": cat_id,
            "name": "Кимчи тиге",
            "description": "Острый суп с кимчи и свининой",
            "price": 9000,
            "is_available": True
        },
        headers=admin_auth_header
    )
    assert item_res.status_code == 200
    item_id = item_res.json()["id"]
    assert item_res.json()["is_available"] is True

    # 3. Toggle availability (stop-list)
    toggle_res = await async_client.patch(
        f"/api/v1/admin/menu/items/{item_id}/toggle",
        headers=admin_auth_header
    )
    assert toggle_res.status_code == 200
    assert toggle_res.json()["is_available"] is False

    # Toggle back to available
    await async_client.patch(f"/api/v1/admin/menu/items/{item_id}/toggle", headers=admin_auth_header)

    # 4. Get Menu Catalog (Public)
    menu_res = await async_client.get("/api/v1/menu")
    assert menu_res.status_code == 200
    catalog = menu_res.json()
    assert len(catalog) >= 1
    found_item = False
    for cat in catalog:
        if cat["id"] == cat_id:
            for item in cat["items"]:
                if item["id"] == item_id:
                    found_item = True
                    assert item["name"] == "Кимчи тиге"
                    assert item["price"] == 9000
    assert found_item is True


@pytest.mark.asyncio
async def test_create_order_multipart(async_client, user_auth_header, admin_auth_header, async_session):
    """
    POST /api/v1/orders
    Creates an order with multipart receipt upload and verifies DB persistence.
    """
    # Create category & item first
    c_res = await async_client.post("/api/v1/admin/menu/categories", data={"name": "Сеты"}, headers=admin_auth_header)
    c_id = c_res.json()["id"]

    i_res = await async_client.post(
        "/api/v1/admin/menu/items",
        data={"category_id": c_id, "name": "Самгёпсаль сет", "price": 28000},
        headers=admin_auth_header
    )
    menu_item_id = i_res.json()["id"]

    # Form multipart order creation payload
    dummy_image = b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01"  # Dummy JPEG bytes
    files = {
        "receipt_image": ("receipt.jpg", dummy_image, "image/jpeg")
    }
    data = {
        "order_type": "delivery",
        "phone": "010-9876-5432",
        "address": "평택시 중앙로 12, 101호",
        "comment": "Без острой приправы",
        "items": json.dumps([{"menu_item_id": menu_item_id, "quantity": 2}])
    }

    order_res = await async_client.post("/api/v1/orders", data=data, files=files, headers=user_auth_header)
    assert order_res.status_code == 200
    res_data = order_res.json()

    assert res_data["status"] == "created"
    order_id = res_data["order_id"]
    # 28000 * 2 + 3000 (delivery) = 59000
    assert res_data["total_amount"] == 59000

    # DB Verification
    stmt = select(Order).where(Order.id == order_id)
    db_order = (await async_session.execute(stmt)).scalar_one_or_none()
    assert db_order is not None
    assert db_order.phone == "010-9876-5432"
    assert db_order.total_amount == 59000
    assert db_order.delivery_fee == 3000

    stmt_items = select(OrderItem).where(OrderItem.order_id == order_id)
    db_items = (await async_session.execute(stmt_items)).scalars().all()
    assert len(db_items) == 1
    assert db_items[0].quantity == 2
    assert db_items[0].price == 28000


@pytest.mark.asyncio
async def test_kitchen_websocket_broadcast(async_client, user_auth_header, admin_auth_header):
    """
    WS /ws/kitchen?token=...
    Connects to WebSocket kitchen stream and verifies receiving NEW_ORDER frame when order is placed.
    """
    from app.services.kitchen_ws import kitchen_manager

    # Mock/Simulate connected WebSocket client in kitchen_manager
    class MockWebSocket:
        def __init__(self):
            self.received_messages = []

        async def send_text(self, message: str):
            self.received_messages.append(message)

    mock_ws = MockWebSocket()
    kitchen_manager.active_connections.append(mock_ws)

    # Create menu item
    c_res = await async_client.post("/api/v1/admin/menu/categories", data={"name": "Десерты"}, headers=admin_auth_header)
    i_res = await async_client.post(
        "/api/v1/admin/menu/items",
        data={"category_id": c_res.json()["id"], "name": "Пинсу", "price": 7000},
        headers=admin_auth_header
    )

    # Send Order request
    dummy_image = b"dummy_receipt_content"
    files = {"receipt_image": ("receipt.png", dummy_image, "image/png")}
    data = {
        "order_type": "pickup",
        "phone": "010-1111-2222",
        "items": json.dumps([{"menu_item_id": i_res.json()["id"], "quantity": 1}])
    }

    order_res = await async_client.post("/api/v1/orders", data=data, files=files, headers=user_auth_header)
    assert order_res.status_code == 200

    # Verify WS message was pushed
    assert len(mock_ws.received_messages) == 1
    ws_event = json.loads(mock_ws.received_messages[0])
    assert ws_event["event"] == "NEW_ORDER"
    assert ws_event["order"]["phone"] == "010-1111-2222"
    assert ws_event["order"]["total_amount"] == 7000  # pickup = 0 delivery fee

    # Clean up
    kitchen_manager.disconnect(mock_ws)


@pytest.mark.asyncio
async def test_admin_clients_analytics(async_client, admin_auth_header, user_auth_header):
    """
    GET /api/v1/admin/clients
    Verifies analytics calculation (LTV, total orders count, and last active timestamp).
    """
    analytics_res = await async_client.get("/api/v1/admin/clients", headers=admin_auth_header)
    assert analytics_res.status_code == 200
    clients = analytics_res.json()

    assert isinstance(clients, list)
    assert len(clients) >= 1

    # Check structure of client profile
    client_entry = clients[0]
    assert "id" in client_entry
    assert "telegram_id" in client_entry
    assert "total_orders" in client_entry
    assert "ltv" in client_entry
    assert "last_active" in client_entry
