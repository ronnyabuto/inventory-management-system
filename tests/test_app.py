import pytest

import database
from app import app


@pytest.fixture(autouse=True)
def reset_data():
    original = [item.copy() for item in database.inventory]
    original_next_id = database._next_id
    yield
    database.inventory.clear()
    database.inventory.extend(original)
    database._next_id = original_next_id


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_get_all_inventory(client):
    r = client.get("/inventory")
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_single_item(client):
    r = client.get("/inventory/1")
    assert r.status_code == 200
    data = r.get_json()
    assert data["id"] == 1
    assert "product_name" in data
    assert "price" in data
    assert "stock_quantity" in data


def test_get_item_not_found(client):
    r = client.get("/inventory/999")
    assert r.status_code == 404
    assert "error" in r.get_json()


def test_create_item(client):
    payload = {
        "product_name": "Test Biscuits",
        "brand": "TestBrand",
        "category": "Snacks",
        "barcode": "1234567890123",
        "price": 2.49,
        "stock_quantity": 50,
        "unit": "200g",
    }
    r = client.post("/inventory", json=payload)
    assert r.status_code == 201
    data = r.get_json()
    assert "id" in data
    assert data["product_name"] == "Test Biscuits"
    assert data["price"] == 2.49
    assert data["stock_quantity"] == 50


def test_create_item_missing_required_field(client):
    payload = {"brand": "TestBrand", "price": 1.99}
    r = client.post("/inventory", json=payload)
    assert r.status_code == 400
    assert "error" in r.get_json()


def test_create_item_no_body(client):
    r = client.post("/inventory", content_type="application/json", data="")
    assert r.status_code == 400


def test_update_item_price(client):
    r = client.patch("/inventory/1", json={"price": 9.99})
    assert r.status_code == 200
    data = r.get_json()
    assert data["id"] == 1
    assert data["price"] == 9.99


def test_update_item_stock(client):
    r = client.patch("/inventory/1", json={"stock_quantity": 500})
    assert r.status_code == 200
    assert r.get_json()["stock_quantity"] == 500


def test_update_item_not_found(client):
    r = client.patch("/inventory/999", json={"price": 1.00})
    assert r.status_code == 404
    assert "error" in r.get_json()


def test_delete_item(client):
    r = client.delete("/inventory/2")
    assert r.status_code == 204
    assert client.get("/inventory/2").status_code == 404


def test_delete_item_not_found(client):
    r = client.delete("/inventory/999")
    assert r.status_code == 404
    assert "error" in r.get_json()


def test_lookup_no_params(client):
    r = client.get("/inventory/lookup")
    assert r.status_code == 400
    assert "error" in r.get_json()
