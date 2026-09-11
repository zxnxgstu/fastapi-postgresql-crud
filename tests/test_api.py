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

def test_admin_can_update_user_role(admin_headers):
    register_response = client.post(
        "/register",
        json={
            "username": "roleuser",
            "email": "roleuser@example.com",
            "password": "password123"
        }
    )

    assert register_response.status_code == 201

    user_id = register_response.json()["id"]

    response = client.patch(
        f"/users/{user_id}/role",
        json={"role": "admin"},
        headers=admin_headers
    )

    assert response.status_code == 200
    assert response.json()["role"] == "admin"


def test_user_cannot_update_roles(auth_headers):
    response = client.patch(
        "/users/999/role",
        json={"role": "admin"},
        headers=auth_headers
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_invalid_user_role(admin_headers):
    response = client.patch(
        "/users/999/role",
        json={"role": "superadmin"},
        headers=admin_headers
    )

    assert response.status_code == 422

def test_get_categories():
    response = client.get("/categories")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_admin_can_create_category(admin_headers):
    response = client.post(
        "/categories",
        json={"name": "Electronics"},
        headers=admin_headers
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Electronics"


def test_user_cannot_create_category(auth_headers):
    response = client.post(
        "/categories",
        json={"name": "Forbidden Category"},
        headers=auth_headers
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_create_product_with_category(auth_headers, admin_headers):
    category_response = client.post(
        "/categories",
        json={"name": "Keyboards"},
        headers=admin_headers
    )

    assert category_response.status_code == 201

    category_id = category_response.json()["id"]

    product_response = client.post(
        "/products",
        json={
            "name": "Mechanical Keyboard",
            "price": 2500,
            "in_stock": True,
            "category_id": category_id
        },
        headers=auth_headers
    )

    assert product_response.status_code == 201
    assert product_response.json()["category_id"] == category_id


def test_create_product_with_missing_category(auth_headers):
    response = client.post(
        "/products",
        json={
            "name": "Invalid Product",
            "price": 1000,
            "in_stock": True,
            "category_id": 999999
        },
        headers=auth_headers
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"

def test_filter_products_by_category(auth_headers, admin_headers):
    category_response = client.post(
        "/categories",
        json={"name": "Monitors"},
        headers=admin_headers
    )

    assert category_response.status_code == 201

    category_id = category_response.json()["id"]

    product_response = client.post(
        "/products",
        json={
            "name": "Gaming Monitor",
            "price": 7000,
            "in_stock": True,
            "category_id": category_id
        },
        headers=auth_headers
    )

    assert product_response.status_code == 201

    response = client.get(
        f"/products?category_id={category_id}"
    )

    assert response.status_code == 200

    products = response.json()

    assert len(products) >= 1
    assert all(
        product["category_id"] == category_id
        for product in products
    )