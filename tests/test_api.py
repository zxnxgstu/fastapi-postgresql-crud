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

def test_get_empty_cart(auth_headers):
    response = client.get(
        "/cart",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json() == []


def test_add_product_to_cart(auth_headers):
    product_response = client.post(
        "/products",
        json={
            "name": "Cart Product",
            "price": 1500,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=auth_headers
    )

    assert product_response.status_code == 201

    product_id = product_response.json()["id"]

    response = client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 2
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    assert response.json()["product_id"] == product_id
    assert response.json()["quantity"] == 2


def test_add_same_product_increases_quantity(auth_headers):
    product_response = client.post(
        "/products",
        json={
            "name": "Repeated Cart Product",
            "price": 2000,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=auth_headers
    )

    product_id = product_response.json()["id"]

    first_response = client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 1
        },
        headers=auth_headers
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 2
        },
        headers=auth_headers
    )

    assert second_response.status_code == 201
    assert second_response.json()["quantity"] == 3

    cart_response = client.get(
        "/cart",
        headers=auth_headers
    )

    cart_items = cart_response.json()

    matching_items = [
        item for item in cart_items
        if item["product_id"] == product_id
    ]

    assert len(matching_items) == 1
    assert matching_items[0]["quantity"] == 3

def test_update_cart_item(auth_headers):
    product_response = client.post(
        "/products",
        json={
            "name": "Update Cart Product",
            "price": 2500,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=auth_headers
    )

    product_id = product_response.json()["id"]

    cart_response = client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 1
        },
        headers=auth_headers
    )

    item_id = cart_response.json()["id"]

    response = client.patch(
        f"/cart/{item_id}",
        json={"quantity": 5},
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["quantity"] == 5


def test_delete_cart_item(auth_headers):
    product_response = client.post(
        "/products",
        json={
            "name": "Delete Cart Product",
            "price": 3000,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=auth_headers
    )

    product_id = product_response.json()["id"]

    cart_response = client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 1
        },
        headers=auth_headers
    )

    item_id = cart_response.json()["id"]

    delete_response = client.delete(
        f"/cart/{item_id}",
        headers=auth_headers
    )

    assert delete_response.status_code == 204

    cart_response = client.get(
        "/cart",
        headers=auth_headers
    )

    assert cart_response.status_code == 200
    remaining_items = cart_response.json()

    assert all(
        item["id"] != item_id
        for item in remaining_items
    )


def test_add_missing_product_to_cart(auth_headers):
    response = client.post(
        "/cart",
        json={
            "product_id": 999999,
            "quantity": 1
        },
        headers=auth_headers
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"

def test_user_cannot_modify_another_users_cart(auth_headers):
    product_response = client.post(
        "/products",
        json={
            "name": "Private Cart Product",
            "price": 1800,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=auth_headers
    )

    product_id = product_response.json()["id"]

    cart_response = client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 1
        },
        headers=auth_headers
    )

    item_id = cart_response.json()["id"]

    client.post(
        "/register",
        json={
            "username": "seconduser",
            "email": "seconduser@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/login",
        data={
            "username": "seconduser",
            "password": "password123"
        }
    )

    second_token = login_response.json()["access_token"]

    second_user_headers = {
        "Authorization": f"Bearer {second_token}"
    }

    response = client.patch(
        f"/cart/{item_id}",
        json={"quantity": 10},
        headers=second_user_headers
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Cart item not found"

def create_test_user(username: str, email: str):
    client.post(
        "/register",
        json={
            "username": username,
            "email": email,
            "password": "password123"
        }
    )

    login_response = client.post(
        "/login",
        data={
            "username": username,
            "password": "password123"
        }
    )

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }

SHIPPING_DATA = {
    "shipping_city": "Kyiv",
    "shipping_street": "Khreshchatyk 1",
    "shipping_postal_code": "01001"
}

def test_create_order_from_cart():
    headers = create_test_user(
        "orderuser1",
        "orderuser1@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Order Product",
            "price": 1500,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 2
        },
        headers=headers
    )

    response = client.post(
        "/orders",
        json=SHIPPING_DATA,
        headers=headers
    )

    assert response.status_code == 201

    order = response.json()

    assert order["total_price"] == 3000
    assert order["status"] == "pending"
    assert len(order["items"]) == 1
    assert order["items"][0]["product_name"] == "Order Product"
    assert order["items"][0]["price"] == 1500
    assert order["items"][0]["quantity"] == 2

    cart_response = client.get(
        "/cart",
        headers=headers
    )

    assert cart_response.status_code == 200
    assert cart_response.json() == []


def test_create_order_with_empty_cart():
    headers = create_test_user(
        "orderuser2",
        "orderuser2@example.com"
    )

    response = client.post(
        "/orders",
        json=SHIPPING_DATA,
        headers=headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Cart is empty"


def test_get_my_orders():
    headers = create_test_user(
        "orderuser3",
        "orderuser3@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "My Orders Product",
            "price": 2000,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 1
        },
        headers=headers
    )

    client.post(
        "/orders",
        json=SHIPPING_DATA,
        headers=headers
    )

    response = client.get(
        "/orders",
        headers=headers
    )

    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_user_cannot_view_another_users_order():
    first_headers = create_test_user(
        "orderuser4",
        "orderuser4@example.com"
    )

    second_headers = create_test_user(
        "orderuser5",
        "orderuser5@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Private Order Product",
            "price": 2500,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=first_headers
    )

    product_id = product_response.json()["id"]

    client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 1
        },
        headers=first_headers
    )

    order_response = client.post(
        "/orders",
        json=SHIPPING_DATA,
        headers=first_headers
    )

    order_id = order_response.json()["id"]

    response = client.get(
        f"/orders/{order_id}",
        headers=second_headers
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


def test_user_cannot_view_admin_orders(auth_headers):
    response = client.get(
        "/admin/orders",
        headers=auth_headers
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_admin_can_view_all_orders(admin_headers):
    response = client.get(
        "/admin/orders",
        headers=admin_headers
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_admin_can_update_order_status(admin_headers):
    headers = create_test_user(
        "orderuser6",
        "orderuser6@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Status Product",
            "price": 3500,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 1
        },
        headers=headers
    )

    order_response = client.post(
        "/orders",
        json=SHIPPING_DATA,
        headers=headers
    )

    order_id = order_response.json()["id"]

    response = client.patch(
        f"/admin/orders/{order_id}/status",
        json={"status": "paid"},
        headers=admin_headers
    )

    assert response.status_code == 200
    assert response.json()["status"] == "paid"


def test_invalid_order_status(admin_headers):
    response = client.patch(
        "/admin/orders/999999/status",
        json={"status": "banana"},
        headers=admin_headers
    )

    assert response.status_code == 422

def test_cannot_add_more_than_stock(auth_headers):
    product_response = client.post(
        "/products",
        json={
            "name": "Limited Product",
            "price": 1000,
            "in_stock": True,
            "stock_quantity": 2
        },
        headers=auth_headers
    )

    product_id = product_response.json()["id"]

    response = client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 3
        },
        headers=auth_headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Not enough stock"


def test_order_decreases_stock(auth_headers):
    product_response = client.post(
        "/products",
        json={
            "name": "Stock Product",
            "price": 2000,
            "in_stock": True,
            "stock_quantity": 5
        },
        headers=auth_headers
    )

    product_id = product_response.json()["id"]

    client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 2
        },
        headers=auth_headers
    )

    order_response = client.post(
        "/orders",
        json=SHIPPING_DATA,
        headers=auth_headers
    )

    assert order_response.status_code == 201

    product_response = client.get(
        f"/products/{product_id}"
    )

    assert product_response.status_code == 200
    assert product_response.json()["stock_quantity"] == 3
    assert product_response.json()["in_stock"] is True


def test_product_becomes_out_of_stock(auth_headers):
    product_response = client.post(
        "/products",
        json={
            "name": "Last Product",
            "price": 3000,
            "in_stock": True,
            "stock_quantity": 1
        },
        headers=auth_headers
    )

    product_id = product_response.json()["id"]

    client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 1
        },
        headers=auth_headers
    )

    order_response = client.post(
        "/orders",
        json=SHIPPING_DATA,
        headers=auth_headers
    )

    assert order_response.status_code == 201

    product_response = client.get(
        f"/products/{product_id}"
    )

    assert product_response.json()["stock_quantity"] == 0
    assert product_response.json()["in_stock"] is False

def test_order_requires_full_shipping_address(auth_headers):
    response = client.post(
        "/orders",
        json={
            "shipping_city": "Kyiv",
            "shipping_street": "Khreshchatyk 1"
        },
        headers=auth_headers
    )

    assert response.status_code == 422

def test_sort_products_by_price_desc(auth_headers):
    client.post(
        "/products",
        json={
            "name": "SortingTest Cheap",
            "price": 1000,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=auth_headers
    )

    client.post(
        "/products",
        json={
            "name": "SortingTest Expensive",
            "price": 3000,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=auth_headers
    )

    response = client.get(
        "/products",
        params={
            "search": "SortingTest",
            "sort_by": "price",
            "order": "desc"
        }
    )

    assert response.status_code == 200

    products = response.json()

    assert products[0]["price"] == 3000
    assert products[1]["price"] == 1000


def test_products_pagination(auth_headers):
    for name in [
        "PaginationTest A",
        "PaginationTest B",
        "PaginationTest C"
    ]:
        client.post(
            "/products",
            json={
                "name": name,
                "price": 1000,
                "in_stock": True,
                "stock_quantity": 10
            },
            headers=auth_headers
        )

    response = client.get(
        "/products",
        params={
            "search": "PaginationTest",
            "sort_by": "id",
            "order": "asc",
            "skip": 1,
            "limit": 1
        }
    )

    assert response.status_code == 200

    products = response.json()

    assert len(products) == 1
    assert products[0]["name"] == "PaginationTest B"


def test_invalid_product_sorting():
    response = client.get(
        "/products",
        params={
            "sort_by": "banana"
        }
    )

    assert response.status_code == 422

def test_products_invalid_negative_skip():
    response = client.get(
        "/products",
        params={
            "skip": -1
        }
    )

    assert response.status_code == 422


def test_products_invalid_limit():
    response = client.get(
        "/products",
        params={
            "limit": 101
        }
    )

    assert response.status_code == 422