from fastapi.testclient import TestClient

from main import app
from tests.conftest import auth_headers

client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200


def test_get_products():
    response = client.get("/products")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_product_validation(auth_headers: dict[str, str]):
    response = client.post(
        "/products",
        json={
            "name": "",
            "price": -100,
            "in_stock": True
        },
        headers=auth_headers
    )

    assert response.status_code == 422


def test_get_missing_product():
    response = client.get("/products/999999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Product not found"
    }


def test_update_missing_product(auth_headers: dict[str, str]):
    response = client.put(
        "/products/999999",
        json={
            "name": "Test",
            "price": 100,
            "in_stock": True
        },
        headers=auth_headers
    )

    assert response.status_code == 404

def test_delete_missing_product(admin_headers: dict[str, str]):
    response = client.delete(
        "/products/999999",
        headers=admin_headers
    )

    assert response.status_code == 404

def test_full_product_crud(auth_headers: dict[str, str], admin_headers: dict[str, str]):
    create_response = client.post(
        "/products",
        json={
            "name": "Test Keyboard",
            "price": 1200,
            "in_stock": True
        },
        headers=admin_headers
    )

    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    get_response = client.get(f"/products/{product_id}")

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Test Keyboard"

    update_response = client.put(
        f"/products/{product_id}",
        json={
            "name": "Updated Keyboard",
            "price": 3000,
            "in_stock": False
        },
        headers=auth_headers
    )

    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Keyboard"
    assert update_response.json()["price"] == 3000
    assert update_response.json()["in_stock"] is False

    delete_response = client.delete(
    f"/products/{product_id}",
    headers=admin_headers
)

    assert delete_response.status_code == 204

    missing_response = client.get(f"/products/{product_id}")

    assert missing_response.status_code == 404

def test_delete_product_forbidden_for_user(auth_headers: dict[str, str]):
    create_response = client.post(
        "/products",
        json={
            "name": "Protected Product",
            "price": 1000,
            "in_stock": True
        },
        headers=auth_headers
    )

    product_id = create_response.json()["id"]

    response = client.delete(
        f"/products/{product_id}",
        headers=auth_headers
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"

def test_get_users_forbidden_for_user(auth_headers):
    response = client.get(
        "/users",
        headers=auth_headers
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"

def test_get_users_for_admin(admin_headers):
    response = client.get(
        "/users",
        headers=admin_headers
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)