from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200


def test_get_products():
    response = client.get("/products")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_product_validation():
    response = client.post(
        "/products",
        json={
            "name": "",
            "price": -100,
            "in_stock": True
        }
    )

    assert response.status_code == 422


def test_get_missing_product():
    response = client.get("/products/999999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Product not found"
    }


def test_update_missing_product():
    response = client.put(
        "/products/999999",
        json={
            "name": "Test Product",
            "price": 100,
            "in_stock": True
        }
    )

    assert response.status_code == 404


def test_delete_missing_product():
    response = client.delete("/products/999999")

    assert response.status_code == 404
def test_full_product_crud():
    create_response = client.post(
        "/products",
        json={
            "name": "Test Keyboard",
            "price": 2500,
            "in_stock": True
        }
    )

    assert create_response.status_code == 201

    created_product = create_response.json()
    product_id = created_product["id"]

    get_response = client.get(f"/products/{product_id}")

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Test Keyboard"

    update_response = client.put(
        f"/products/{product_id}",
        json={
            "name": "Updated Keyboard",
            "price": 3000,
            "in_stock": False
        }
    )

    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Keyboard"
    assert update_response.json()["price"] == 3000
    assert update_response.json()["in_stock"] is False

    delete_response = client.delete(f"/products/{product_id}")

    assert delete_response.status_code == 204

    missing_response = client.get(f"/products/{product_id}")

    assert missing_response.status_code == 404