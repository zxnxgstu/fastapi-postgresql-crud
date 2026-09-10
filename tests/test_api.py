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