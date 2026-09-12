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

    payment_response = client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    assert payment_response.status_code == 201

    response = client.patch(
        f"/admin/orders/{order_id}/status",
        json={
            "status": "shipped"
        },
        headers=admin_headers
    )

    assert response.status_code == 200
    assert response.json()["status"] == "shipped"


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

def test_filter_my_orders_by_status(admin_headers):
    headers = create_test_user(
        "orderfilteruser",
        "orderfilteruser@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Order Filter Product",
            "price": 1500,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    # Первый заказ оставляем pending
    client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 1
        },
        headers=headers
    )

    pending_order = client.post(
        "/orders",
        json=SHIPPING_DATA,
        headers=headers
    )

    assert pending_order.status_code == 201

    # Второй заказ доводим до completed
    client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 1
        },
        headers=headers
    )

    completed_order = client.post(
        "/orders",
        json=SHIPPING_DATA,
        headers=headers
    )

    assert completed_order.status_code == 201

    completed_order_id = completed_order.json()["id"]

    payment_response = client.post(
        f"/orders/{completed_order_id}/pay",
        headers=headers
    )

    assert payment_response.status_code == 201

    shipped_response = client.patch(
        f"/admin/orders/{completed_order_id}/status",
        json={
            "status": "shipped"
        },
        headers=admin_headers
    )

    assert shipped_response.status_code == 200

    completed_response = client.patch(
        f"/admin/orders/{completed_order_id}/status",
        json={
            "status": "completed"
        },
        headers=admin_headers
    )

    assert completed_response.status_code == 200

    response = client.get(
        "/orders",
        params={
            "status": "completed"
        },
        headers=headers
    )

    assert response.status_code == 200

    orders = response.json()

    assert len(orders) == 1
    assert orders[0]["id"] == completed_order_id
    assert orders[0]["status"] == "completed"


def test_admin_orders_pagination(admin_headers):
    response = client.get(
        "/admin/orders",
        params={
            "skip": 0,
            "limit": 1
        },
        headers=admin_headers
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_invalid_order_status_filter(auth_headers):
    response = client.get(
        "/orders",
        params={
            "status": "banana"
        },
        headers=auth_headers
    )

    assert response.status_code == 422

def test_admin_can_create_promo_code(admin_headers):
    response = client.post(
        "/promo-codes",
        json={
            "code": "SALE10",
            "discount_percent": 10,
            "active": True
        },
        headers=admin_headers
    )

    assert response.status_code == 201

    promo_code = response.json()

    assert promo_code["code"] == "SALE10"
    assert promo_code["discount_percent"] == 10
    assert promo_code["active"] is True


def test_user_cannot_create_promo_code(auth_headers):
    response = client.post(
        "/promo-codes",
        json={
            "code": "USER20",
            "discount_percent": 20,
            "active": True
        },
        headers=auth_headers
    )

    assert response.status_code == 403


def test_duplicate_promo_code(admin_headers):
    client.post(
        "/promo-codes",
        json={
            "code": "DUPLICATE15",
            "discount_percent": 15,
            "active": True
        },
        headers=admin_headers
    )

    response = client.post(
        "/promo-codes",
        json={
            "code": "DUPLICATE15",
            "discount_percent": 15,
            "active": True
        },
        headers=admin_headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Promo code already exists"


def test_get_active_promo_code(admin_headers):
    client.post(
        "/promo-codes",
        json={
            "code": "CHECK25",
            "discount_percent": 25,
            "active": True
        },
        headers=admin_headers
    )

    response = client.get(
        "/promo-codes/CHECK25"
    )

    assert response.status_code == 200

    promo_code = response.json()

    assert promo_code["code"] == "CHECK25"
    assert promo_code["discount_percent"] == 25

def test_order_applies_promo_code(admin_headers):
    headers = create_test_user(
        "promouser1",
        "promouser1@example.com"
    )

    client.post(
        "/promo-codes",
        json={
            "code": "ORDER10",
            "discount_percent": 10,
            "active": True
        },
        headers=admin_headers
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Promo Product",
            "price": 1000,
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

    response = client.post(
        "/orders",
        json={
            "shipping_city": "Kyiv",
            "shipping_street": "Khreshchatyk 1",
            "shipping_postal_code": "01001",
            "promo_code": "ORDER10"
        },
        headers=headers
    )

    assert response.status_code == 201

    order = response.json()

    assert order["total_price"] == 900
    assert order["promo_code"] == "ORDER10"
    assert order["discount_percent"] == 10


def test_order_with_invalid_promo_code():
    headers = create_test_user(
        "promouser2",
        "promouser2@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Invalid Promo Product",
            "price": 1000,
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

    response = client.post(
        "/orders",
        json={
            "shipping_city": "Kyiv",
            "shipping_street": "Khreshchatyk 1",
            "shipping_postal_code": "01001",
            "promo_code": "DOESNOTEXIST"
        },
        headers=headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid promo code"


def test_inactive_promo_code_cannot_be_used(admin_headers):
    headers = create_test_user(
        "promouser3",
        "promouser3@example.com"
    )

    client.post(
        "/promo-codes",
        json={
            "code": "INACTIVE20",
            "discount_percent": 20,
            "active": False
        },
        headers=admin_headers
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Inactive Promo Product",
            "price": 1000,
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

    response = client.post(
        "/orders",
        json={
            "shipping_city": "Kyiv",
            "shipping_street": "Khreshchatyk 1",
            "shipping_postal_code": "01001",
            "promo_code": "INACTIVE20"
        },
        headers=headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid promo code"

def test_cancel_order_restores_stock():
    headers = create_test_user(
        "canceluser1",
        "canceluser1@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Cancel Stock Product",
            "price": 1000,
            "in_stock": True,
            "stock_quantity": 5
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

    order_response = client.post(
        "/orders",
        json=SHIPPING_DATA,
        headers=headers
    )

    order_id = order_response.json()["id"]

    product_after_order = client.get(
        f"/products/{product_id}"
    ).json()

    assert product_after_order["stock_quantity"] == 3

    cancel_response = client.post(
        f"/orders/{order_id}/cancel",
        headers=headers
    )

    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"

    product_after_cancel = client.get(
        f"/products/{product_id}"
    ).json()

    assert product_after_cancel["stock_quantity"] == 5
    assert product_after_cancel["in_stock"] is True


def test_cannot_cancel_order_twice():
    headers = create_test_user(
        "canceluser2",
        "canceluser2@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Cancel Twice Product",
            "price": 1000,
            "in_stock": True,
            "stock_quantity": 5
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

    client.post(
        f"/orders/{order_id}/cancel",
        headers=headers
    )

    response = client.post(
        f"/orders/{order_id}/cancel",
        headers=headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Order already cancelled"


def test_user_cannot_cancel_completed_order(admin_headers):
    headers = create_test_user(
        "canceluser3",
        "canceluser3@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Completed Order Product",
            "price": 1000,
            "in_stock": True,
            "stock_quantity": 5
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

    payment_response = client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    assert payment_response.status_code == 201

    shipped_response = client.patch(
        f"/admin/orders/{order_id}/status",
        json={
            "status": "shipped"
        },
        headers=admin_headers
    )

    assert shipped_response.status_code == 200

    completed_response = client.patch(
        f"/admin/orders/{order_id}/status",
        json={
            "status": "completed"
        },
        headers=admin_headers
    )

    assert completed_response.status_code == 200

    response = client.post(
        f"/orders/{order_id}/cancel",
        headers=headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Completed order cannot be cancelled"

def test_admin_can_cancel_order(admin_headers):
    headers = create_test_user(
        "admincanceluser1",
        "admincanceluser1@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Admin Cancel Product",
            "price": 1000,
            "in_stock": True,
            "stock_quantity": 5
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

    order_response = client.post(
        "/orders",
        json=SHIPPING_DATA,
        headers=headers
    )

    order_id = order_response.json()["id"]

    response = client.post(
        f"/admin/orders/{order_id}/cancel",
        headers=admin_headers
    )

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"

    product_response = client.get(
        f"/products/{product_id}"
    )

    assert product_response.json()["stock_quantity"] == 5


def test_admin_cannot_cancel_order_via_status_patch(admin_headers):
    headers = create_test_user(
        "admincanceluser2",
        "admincanceluser2@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Admin Patch Cancel Product",
            "price": 1000,
            "in_stock": True,
            "stock_quantity": 5
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
        json={
            "status": "cancelled"
        },
        headers=admin_headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Use cancel endpoint to cancel orders"

def test_add_product_to_wishlist():
    headers = create_test_user(
        "wishlistuser1",
        "wishlistuser1@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Wishlist Product",
            "price": 1000,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    response = client.post(
        "/wishlist",
        json={
            "product_id": product_id
        },
        headers=headers
    )

    assert response.status_code == 201
    assert response.json()["product_id"] == product_id


def test_cannot_add_duplicate_wishlist_item():
    headers = create_test_user(
        "wishlistuser2",
        "wishlistuser2@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Wishlist Duplicate Product",
            "price": 1500,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    client.post(
        "/wishlist",
        json={
            "product_id": product_id
        },
        headers=headers
    )

    response = client.post(
        "/wishlist",
        json={
            "product_id": product_id
        },
        headers=headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Product already in wishlist"


def test_remove_product_from_wishlist():
    headers = create_test_user(
        "wishlistuser3",
        "wishlistuser3@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Wishlist Remove Product",
            "price": 2000,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    client.post(
        "/wishlist",
        json={
            "product_id": product_id
        },
        headers=headers
    )

    response = client.delete(
        f"/wishlist/{product_id}",
        headers=headers
    )

    assert response.status_code == 204

    wishlist_response = client.get(
        "/wishlist",
        headers=headers
    )

    assert wishlist_response.status_code == 200
    assert wishlist_response.json() == []


def test_users_have_separate_wishlists():
    headers1 = create_test_user(
        "wishlistuser4",
        "wishlistuser4@example.com"
    )

    headers2 = create_test_user(
        "wishlistuser5",
        "wishlistuser5@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Private Wishlist Product",
            "price": 2500,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers1
    )

    product_id = product_response.json()["id"]

    client.post(
        "/wishlist",
        json={
            "product_id": product_id
        },
        headers=headers1
    )

    response = client.get(
        "/wishlist",
        headers=headers2
    )

    assert response.status_code == 200
    assert response.json() == []

def test_create_product_review():
    headers = create_test_user(
        "reviewuser1",
        "reviewuser1@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Review Product 1",
            "price": 1000,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    response = client.post(
        f"/products/{product_id}/reviews",
        json={
            "rating": 5,
            "comment": "Great product"
        },
        headers=headers
    )

    assert response.status_code == 201

    review = response.json()

    assert review["product_id"] == product_id
    assert review["rating"] == 5
    assert review["comment"] == "Great product"


def test_invalid_review_rating():
    headers = create_test_user(
        "reviewuser2",
        "reviewuser2@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Review Product 2",
            "price": 1200,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    response = client.post(
        f"/products/{product_id}/reviews",
        json={
            "rating": 6,
            "comment": "Invalid rating"
        },
        headers=headers
    )

    assert response.status_code == 422


def test_cannot_review_product_twice():
    headers = create_test_user(
        "reviewuser3",
        "reviewuser3@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Review Product 3",
            "price": 1500,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    client.post(
        f"/products/{product_id}/reviews",
        json={
            "rating": 4,
            "comment": "First review"
        },
        headers=headers
    )

    response = client.post(
        f"/products/{product_id}/reviews",
        json={
            "rating": 5,
            "comment": "Second review"
        },
        headers=headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "You already reviewed this product"


def test_update_own_review():
    headers = create_test_user(
        "reviewuser4",
        "reviewuser4@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Review Product 4",
            "price": 2000,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    review_response = client.post(
        f"/products/{product_id}/reviews",
        json={
            "rating": 3,
            "comment": "Normal"
        },
        headers=headers
    )

    review_id = review_response.json()["id"]

    response = client.patch(
        f"/products/reviews/{review_id}",
        json={
            "rating": 5,
            "comment": "Much better"
        },
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["rating"] == 5
    assert response.json()["comment"] == "Much better"


def test_delete_own_review():
    headers = create_test_user(
        "reviewuser5",
        "reviewuser5@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Review Product 5",
            "price": 2500,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    review_response = client.post(
        f"/products/{product_id}/reviews",
        json={
            "rating": 4,
            "comment": "Delete me"
        },
        headers=headers
    )

    review_id = review_response.json()["id"]

    response = client.delete(
        f"/products/reviews/{review_id}",
        headers=headers
    )

    assert response.status_code == 204

    reviews_response = client.get(
        f"/products/{product_id}/reviews"
    )

    assert reviews_response.status_code == 200
    assert reviews_response.json() == []

def test_product_average_rating_and_reviews_count():
    headers1 = create_test_user(
        "ratinguser1",
        "ratinguser1@example.com"
    )

    headers2 = create_test_user(
        "ratinguser2",
        "ratinguser2@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Rating Product",
            "price": 3000,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers1
    )

    product_id = product_response.json()["id"]

    client.post(
        f"/products/{product_id}/reviews",
        json={
            "rating": 5,
            "comment": "Excellent"
        },
        headers=headers1
    )

    client.post(
        f"/products/{product_id}/reviews",
        json={
            "rating": 3,
            "comment": "Okay"
        },
        headers=headers2
    )

    response = client.get(
        f"/products/{product_id}"
    )

    assert response.status_code == 200

    product = response.json()

    assert product["average_rating"] == 4.0
    assert product["reviews_count"] == 2

def test_product_price_history(admin_headers):
    product_response = client.post(
        "/products",
        json={
            "name": "Price History Product",
            "price": 3000,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=admin_headers
    )

    product_id = product_response.json()["id"]

    client.put(
        f"/products/{product_id}",
        json={
            "name": "Price History Product",
            "price": 2500,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=admin_headers
    )

    client.put(
        f"/products/{product_id}",
        json={
            "name": "Price History Product",
            "price": 2000,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=admin_headers
    )

    response = client.get(
        f"/products/{product_id}/price-history"
    )

    assert response.status_code == 200

    history = response.json()

    assert len(history) == 2

    assert history[0]["old_price"] == 2500
    assert history[0]["new_price"] == 2000

    assert history[1]["old_price"] == 3000
    assert history[1]["new_price"] == 2500


def test_same_price_does_not_create_price_history(admin_headers):
    product_response = client.post(
        "/products",
        json={
            "name": "Same Price Product",
            "price": 4000,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=admin_headers
    )

    product_id = product_response.json()["id"]

    client.put(
        f"/products/{product_id}",
        json={
            "name": "Same Price Product Updated",
            "price": 4000,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=admin_headers
    )

    response = client.get(
        f"/products/{product_id}/price-history"
    )

    assert response.status_code == 200
    assert response.json() == []

def test_price_drop_creates_notification(admin_headers):
    headers = create_test_user(
        "notifyuser1",
        "notifyuser1@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Notification Product",
            "price": 3000,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    client.post(
        "/wishlist",
        json={
            "product_id": product_id
        },
        headers=headers
    )

    client.put(
        f"/products/{product_id}",
        json={
            "name": "Notification Product",
            "price": 2500,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=admin_headers
    )

    response = client.get(
        "/notifications",
        headers=headers
    )

    assert response.status_code == 200

    notifications = response.json()

    assert len(notifications) == 1
    assert notifications[0]["product_id"] == product_id
    assert notifications[0]["old_price"] == 3000
    assert notifications[0]["new_price"] == 2500
    assert notifications[0]["is_read"] is False


def test_price_increase_does_not_create_notification(admin_headers):
    headers = create_test_user(
        "notifyuser2",
        "notifyuser2@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "No Notification Product",
            "price": 2000,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    client.post(
        "/wishlist",
        json={
            "product_id": product_id
        },
        headers=headers
    )

    client.put(
        f"/products/{product_id}",
        json={
            "name": "No Notification Product",
            "price": 2500,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=admin_headers
    )

    response = client.get(
        "/notifications",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json() == []


def test_mark_price_drop_notification_as_read(admin_headers):
    headers = create_test_user(
        "notifyuser3",
        "notifyuser3@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Read Notification Product",
            "price": 5000,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    client.post(
        "/wishlist",
        json={
            "product_id": product_id
        },
        headers=headers
    )

    client.put(
        f"/products/{product_id}",
        json={
            "name": "Read Notification Product",
            "price": 4000,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=admin_headers
    )

    notifications_response = client.get(
        "/notifications",
        headers=headers
    )

    notification_id = notifications_response.json()[0]["id"]

    response = client.patch(
        f"/notifications/{notification_id}/read",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["is_read"] is True

def test_user_can_pay_order():
    headers = create_test_user(
        "paymentuser1",
        "paymentuser1@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Payment Product",
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
            "quantity": 2
        },
        headers=headers
    )

    order_response = client.post(
        "/orders",
        json=SHIPPING_DATA,
        headers=headers
    )

    order_id = order_response.json()["id"]

    response = client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    assert response.status_code == 201

    payment = response.json()

    assert payment["order_id"] == order_id
    assert payment["amount"] == 4000
    assert payment["status"] == "paid"


def test_order_cannot_be_paid_twice():
    headers = create_test_user(
        "paymentuser2",
        "paymentuser2@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Double Payment Product",
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

    first_response = client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    assert first_response.status_code == 201

    response = client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Order already paid"


def test_user_cannot_pay_another_users_order():
    headers1 = create_test_user(
        "paymentuser3",
        "paymentuser3@example.com"
    )

    headers2 = create_test_user(
        "paymentuser4",
        "paymentuser4@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Private Payment Product",
            "price": 1800,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers1
    )

    product_id = product_response.json()["id"]

    client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 1
        },
        headers=headers1
    )

    order_response = client.post(
        "/orders",
        json=SHIPPING_DATA,
        headers=headers1
    )

    order_id = order_response.json()["id"]

    response = client.post(
        f"/orders/{order_id}/pay",
        headers=headers2
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


def test_cancelled_order_cannot_be_paid():
    headers = create_test_user(
        "paymentuser5",
        "paymentuser5@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Cancelled Payment Product",
            "price": 2200,
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

    cancel_response = client.post(
        f"/orders/{order_id}/cancel",
        headers=headers
    )

    assert cancel_response.status_code == 200

    response = client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Cancelled order cannot be paid"

def test_refund_paid_order_restores_stock():
    headers = create_test_user(
        "refunduser1",
        "refunduser1@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Refund Product",
            "price": 2000,
            "in_stock": True,
            "stock_quantity": 5
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

    order_response = client.post(
        "/orders",
        json=SHIPPING_DATA,
        headers=headers
    )

    order_id = order_response.json()["id"]

    payment_response = client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    assert payment_response.status_code == 201

    product_after_order = client.get(
        f"/products/{product_id}"
    ).json()

    assert product_after_order["stock_quantity"] == 3

    response = client.post(
        f"/orders/{order_id}/refund",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["status"] == "refunded"
    assert response.json()["amount"] == 4000

    product_after_refund = client.get(
        f"/products/{product_id}"
    ).json()

    assert product_after_refund["stock_quantity"] == 5
    assert product_after_refund["in_stock"] is True

    order_after_refund = client.get(
        f"/orders/{order_id}",
        headers=headers
    )

    assert order_after_refund.status_code == 200
    assert order_after_refund.json()["status"] == "cancelled"


def test_payment_cannot_be_refunded_twice():
    headers = create_test_user(
        "refunduser2",
        "refunduser2@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Double Refund Product",
            "price": 1500,
            "in_stock": True,
            "stock_quantity": 5
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

    client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    first_refund = client.post(
        f"/orders/{order_id}/refund",
        headers=headers
    )

    assert first_refund.status_code == 200

    response = client.post(
        f"/orders/{order_id}/refund",
        headers=headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Payment already refunded"


def test_user_cannot_refund_another_users_order():
    headers1 = create_test_user(
        "refunduser3",
        "refunduser3@example.com"
    )

    headers2 = create_test_user(
        "refunduser4",
        "refunduser4@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Private Refund Product",
            "price": 1800,
            "in_stock": True,
            "stock_quantity": 5
        },
        headers=headers1
    )

    product_id = product_response.json()["id"]

    client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 1
        },
        headers=headers1
    )

    order_response = client.post(
        "/orders",
        json=SHIPPING_DATA,
        headers=headers1
    )

    order_id = order_response.json()["id"]

    client.post(
        f"/orders/{order_id}/pay",
        headers=headers1
    )

    response = client.post(
        f"/orders/{order_id}/refund",
        headers=headers2
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


def test_paid_order_must_use_refund_instead_of_cancel():
    headers = create_test_user(
        "refunduser5",
        "refunduser5@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Paid Cancel Product",
            "price": 2500,
            "in_stock": True,
            "stock_quantity": 5
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

    client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    response = client.post(
        f"/orders/{order_id}/cancel",
        headers=headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Paid order must be refunded"

def test_cannot_change_pending_order_directly_to_completed(admin_headers):
    headers = create_test_user(
        "workflowuser1",
        "workflowuser1@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Workflow Product 1",
            "price": 1000,
            "in_stock": True,
            "stock_quantity": 5
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
        json={
            "status": "completed"
        },
        headers=admin_headers
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Cannot change order status from pending to completed"
    )


def test_cannot_change_pending_order_directly_to_shipped(admin_headers):
    headers = create_test_user(
        "workflowuser2",
        "workflowuser2@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Workflow Product 2",
            "price": 1200,
            "in_stock": True,
            "stock_quantity": 5
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
        json={
            "status": "shipped"
        },
        headers=admin_headers
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Cannot change order status from pending to shipped"
    )


def test_completed_order_status_cannot_be_changed(admin_headers):
    headers = create_test_user(
        "workflowuser3",
        "workflowuser3@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Workflow Product 3",
            "price": 1500,
            "in_stock": True,
            "stock_quantity": 5
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

    payment_response = client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    assert payment_response.status_code == 201

    shipped_response = client.patch(
        f"/admin/orders/{order_id}/status",
        json={
            "status": "shipped"
        },
        headers=admin_headers
    )

    assert shipped_response.status_code == 200

    completed_response = client.patch(
        f"/admin/orders/{order_id}/status",
        json={
            "status": "completed"
        },
        headers=admin_headers
    )

    assert completed_response.status_code == 200

    response = client.patch(
        f"/admin/orders/{order_id}/status",
        json={
            "status": "shipped"
        },
        headers=admin_headers
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Cannot change order status from completed to shipped"
    )

def test_order_status_history_tracks_full_workflow(admin_headers):
    headers = create_test_user(
        "historyuser1",
        "historyuser1@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Status History Product",
            "price": 2000,
            "in_stock": True,
            "stock_quantity": 5
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

    assert order_response.status_code == 201

    order_id = order_response.json()["id"]

    payment_response = client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    assert payment_response.status_code == 201

    shipped_response = client.patch(
        f"/admin/orders/{order_id}/status",
        json={
            "status": "shipped"
        },
        headers=admin_headers
    )

    assert shipped_response.status_code == 200

    completed_response = client.patch(
        f"/admin/orders/{order_id}/status",
        json={
            "status": "completed"
        },
        headers=admin_headers
    )

    assert completed_response.status_code == 200

    response = client.get(
        f"/orders/{order_id}/status-history",
        headers=headers
    )

    assert response.status_code == 200

    history = response.json()

    assert len(history) == 4

    assert history[0]["old_status"] is None
    assert history[0]["new_status"] == "pending"

    assert history[1]["old_status"] == "pending"
    assert history[1]["new_status"] == "paid"

    assert history[2]["old_status"] == "paid"
    assert history[2]["new_status"] == "shipped"

    assert history[3]["old_status"] == "shipped"
    assert history[3]["new_status"] == "completed"


def test_user_cannot_view_another_users_order_status_history():
    headers1 = create_test_user(
        "historyuser2",
        "historyuser2@example.com"
    )

    headers2 = create_test_user(
        "historyuser3",
        "historyuser3@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Private History Product",
            "price": 1500,
            "in_stock": True,
            "stock_quantity": 5
        },
        headers=headers1
    )

    product_id = product_response.json()["id"]

    client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 1
        },
        headers=headers1
    )

    order_response = client.post(
        "/orders",
        json=SHIPPING_DATA,
        headers=headers1
    )

    assert order_response.status_code == 201

    order_id = order_response.json()["id"]

    response = client.get(
        f"/orders/{order_id}/status-history",
        headers=headers2
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"

def test_order_status_history_tracks_cancel():
    headers = create_test_user(
        "historycanceluser",
        "historycanceluser@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Cancel History Product",
            "price": 1000,
            "in_stock": True,
            "stock_quantity": 5
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

    assert order_response.status_code == 201

    order_id = order_response.json()["id"]

    cancel_response = client.post(
        f"/orders/{order_id}/cancel",
        headers=headers
    )

    assert cancel_response.status_code == 200

    response = client.get(
        f"/orders/{order_id}/status-history",
        headers=headers
    )

    assert response.status_code == 200

    history = response.json()

    assert len(history) == 2

    assert history[0]["old_status"] is None
    assert history[0]["new_status"] == "pending"

    assert history[1]["old_status"] == "pending"
    assert history[1]["new_status"] == "cancelled"


def test_order_status_history_tracks_refund():
    headers = create_test_user(
        "historyrefunduser",
        "historyrefunduser@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Refund History Product",
            "price": 2500,
            "in_stock": True,
            "stock_quantity": 5
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

    assert order_response.status_code == 201

    order_id = order_response.json()["id"]

    payment_response = client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    assert payment_response.status_code == 201

    refund_response = client.post(
        f"/orders/{order_id}/refund",
        headers=headers
    )

    assert refund_response.status_code == 200
    assert refund_response.json()["status"] == "refunded"

    response = client.get(
        f"/orders/{order_id}/status-history",
        headers=headers
    )

    assert response.status_code == 200

    history = response.json()

    assert len(history) == 3

    assert history[0]["old_status"] is None
    assert history[0]["new_status"] == "pending"

    assert history[1]["old_status"] == "pending"
    assert history[1]["new_status"] == "paid"

    assert history[2]["old_status"] == "paid"
    assert history[2]["new_status"] == "cancelled"

def test_create_first_address_becomes_default():
    headers = create_test_user(
        "addressuser1",
        "addressuser1@example.com"
    )

    response = client.post(
        "/addresses",
        json={
            "city": "Kyiv",
            "street": "Khreshchatyk 1",
            "postal_code": "01001",
            "is_default": False
        },
        headers=headers
    )

    assert response.status_code == 201

    address = response.json()

    assert address["city"] == "Kyiv"
    assert address["street"] == "Khreshchatyk 1"
    assert address["postal_code"] == "01001"
    assert address["is_default"] is True


def test_get_user_addresses():
    headers = create_test_user(
        "addressuser2",
        "addressuser2@example.com"
    )

    client.post(
        "/addresses",
        json={
            "city": "Dnipro",
            "street": "Centralna 10",
            "postal_code": "49000",
            "is_default": False
        },
        headers=headers
    )

    client.post(
        "/addresses",
        json={
            "city": "Lviv",
            "street": "Shevchenka 20",
            "postal_code": "79000",
            "is_default": False
        },
        headers=headers
    )

    response = client.get(
        "/addresses",
        headers=headers
    )

    assert response.status_code == 200

    addresses = response.json()

    assert len(addresses) == 2
    assert addresses[0]["is_default"] is True
    assert addresses[0]["city"] == "Dnipro"
    assert addresses[1]["city"] == "Lviv"


def test_user_can_change_default_address():
    headers = create_test_user(
        "addressuser3",
        "addressuser3@example.com"
    )

    first_response = client.post(
        "/addresses",
        json={
            "city": "Kyiv",
            "street": "Street 1",
            "postal_code": "01001",
            "is_default": False
        },
        headers=headers
    )

    first_id = first_response.json()["id"]

    second_response = client.post(
        "/addresses",
        json={
            "city": "Odesa",
            "street": "Street 2",
            "postal_code": "65000",
            "is_default": False
        },
        headers=headers
    )

    second_id = second_response.json()["id"]

    response = client.patch(
        f"/addresses/{second_id}",
        json={
            "city": "Odesa",
            "street": "Street 2",
            "postal_code": "65000",
            "is_default": True
        },
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["is_default"] is True

    addresses_response = client.get(
        "/addresses",
        headers=headers
    )

    addresses = addresses_response.json()

    first_address = next(
        address
        for address in addresses
        if address["id"] == first_id
    )

    second_address = next(
        address
        for address in addresses
        if address["id"] == second_id
    )

    assert first_address["is_default"] is False
    assert second_address["is_default"] is True


def test_delete_default_address_selects_next_default():
    headers = create_test_user(
        "addressuser4",
        "addressuser4@example.com"
    )

    first_response = client.post(
        "/addresses",
        json={
            "city": "Kyiv",
            "street": "Default Street",
            "postal_code": "01001",
            "is_default": False
        },
        headers=headers
    )

    first_id = first_response.json()["id"]

    second_response = client.post(
        "/addresses",
        json={
            "city": "Kharkiv",
            "street": "Second Street",
            "postal_code": "61000",
            "is_default": False
        },
        headers=headers
    )

    second_id = second_response.json()["id"]

    delete_response = client.delete(
        f"/addresses/{first_id}",
        headers=headers
    )

    assert delete_response.status_code == 204

    response = client.get(
        "/addresses",
        headers=headers
    )

    assert response.status_code == 200

    addresses = response.json()

    assert len(addresses) == 1
    assert addresses[0]["id"] == second_id
    assert addresses[0]["is_default"] is True


def test_user_cannot_modify_another_users_address():
    headers1 = create_test_user(
        "addressuser5",
        "addressuser5@example.com"
    )

    headers2 = create_test_user(
        "addressuser6",
        "addressuser6@example.com"
    )

    address_response = client.post(
        "/addresses",
        json={
            "city": "Kyiv",
            "street": "Private Street",
            "postal_code": "01001",
            "is_default": False
        },
        headers=headers1
    )

    address_id = address_response.json()["id"]

    update_response = client.patch(
        f"/addresses/{address_id}",
        json={
            "city": "Changed City",
            "street": "Changed Street",
            "postal_code": "99999",
            "is_default": True
        },
        headers=headers2
    )

    assert update_response.status_code == 404
    assert update_response.json()["detail"] == "Address not found"

    delete_response = client.delete(
        f"/addresses/{address_id}",
        headers=headers2
    )

    assert delete_response.status_code == 404
    assert delete_response.json()["detail"] == "Address not found"

def test_create_order_with_saved_address():
    headers = create_test_user(
        "orderaddressuser1",
        "orderaddressuser1@example.com"
    )

    address_response = client.post(
        "/addresses",
        json={
            "city": "Kyiv",
            "street": "Saved Street 15",
            "postal_code": "01001",
            "is_default": True
        },
        headers=headers
    )

    assert address_response.status_code == 201

    address_id = address_response.json()["id"]

    product_response = client.post(
        "/products",
        json={
            "name": "Saved Address Product",
            "price": 2000,
            "in_stock": True,
            "stock_quantity": 5
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

    response = client.post(
        "/orders",
        json={
            "address_id": address_id
        },
        headers=headers
    )

    assert response.status_code == 201

    order = response.json()

    assert order["shipping_city"] == "Kyiv"
    assert order["shipping_street"] == "Saved Street 15"
    assert order["shipping_postal_code"] == "01001"


def test_user_cannot_create_order_with_another_users_address():
    headers1 = create_test_user(
        "orderaddressuser2",
        "orderaddressuser2@example.com"
    )

    headers2 = create_test_user(
        "orderaddressuser3",
        "orderaddressuser3@example.com"
    )

    address_response = client.post(
        "/addresses",
        json={
            "city": "Lviv",
            "street": "Private Street 20",
            "postal_code": "79000",
            "is_default": True
        },
        headers=headers1
    )

    assert address_response.status_code == 201

    address_id = address_response.json()["id"]

    product_response = client.post(
        "/products",
        json={
            "name": "Foreign Address Product",
            "price": 1500,
            "in_stock": True,
            "stock_quantity": 5
        },
        headers=headers2
    )

    product_id = product_response.json()["id"]

    client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 1
        },
        headers=headers2
    )

    response = client.post(
        "/orders",
        json={
            "address_id": address_id
        },
        headers=headers2
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Address not found"

def test_create_order_uses_default_address_automatically():
    headers = create_test_user(
        "defaultaddressuser1",
        "defaultaddressuser1@example.com"
    )

    address_response = client.post(
        "/addresses",
        json={
            "city": "Kyiv",
            "street": "Default Street 25",
            "postal_code": "01001",
            "is_default": False
        },
        headers=headers
    )

    assert address_response.status_code == 201
    assert address_response.json()["is_default"] is True

    product_response = client.post(
        "/products",
        json={
            "name": "Default Address Product",
            "price": 1800,
            "in_stock": True,
            "stock_quantity": 5
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

    response = client.post(
        "/orders",
        json={},
        headers=headers
    )

    assert response.status_code == 201

    order = response.json()

    assert order["shipping_city"] == "Kyiv"
    assert order["shipping_street"] == "Default Street 25"
    assert order["shipping_postal_code"] == "01001"


def test_create_order_without_address_fails_when_no_default_address():
    headers = create_test_user(
        "defaultaddressuser2",
        "defaultaddressuser2@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "No Default Address Product",
            "price": 1200,
            "in_stock": True,
            "stock_quantity": 5
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

    response = client.post(
        "/orders",
        json={},
        headers=headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Default address not found"

def test_admin_can_create_delivery_method(admin_headers):
    response = client.post(
        "/delivery-methods",
        json={
            "code": "standard_test",
            "name": "Standard Test Delivery",
            "price": 100,
            "active": True
        },
        headers=admin_headers
    )

    assert response.status_code == 201

    delivery_method = response.json()

    assert delivery_method["code"] == "standard_test"
    assert delivery_method["name"] == "Standard Test Delivery"
    assert delivery_method["price"] == 100
    assert delivery_method["active"] is True


def test_user_cannot_create_delivery_method():
    headers = create_test_user(
        "deliveryuser1",
        "deliveryuser1@example.com"
    )

    response = client.post(
        "/delivery-methods",
        json={
            "code": "forbidden_delivery",
            "name": "Forbidden Delivery",
            "price": 150,
            "active": True
        },
        headers=headers
    )

    assert response.status_code == 403


def test_public_delivery_methods_show_only_active(admin_headers):
    active_response = client.post(
        "/delivery-methods",
        json={
            "code": "active_delivery_test",
            "name": "Active Delivery Test",
            "price": 200,
            "active": True
        },
        headers=admin_headers
    )

    assert active_response.status_code == 201

    inactive_response = client.post(
        "/delivery-methods",
        json={
            "code": "inactive_delivery_test",
            "name": "Inactive Delivery Test",
            "price": 300,
            "active": False
        },
        headers=admin_headers
    )

    assert inactive_response.status_code == 201

    public_response = client.get(
        "/delivery-methods"
    )

    assert public_response.status_code == 200

    public_methods = public_response.json()

    public_codes = [
        method["code"]
        for method in public_methods
    ]

    assert "active_delivery_test" in public_codes
    assert "inactive_delivery_test" not in public_codes

    admin_response = client.get(
        "/delivery-methods/admin",
        headers=admin_headers
    )

    assert admin_response.status_code == 200

    admin_methods = admin_response.json()

    admin_codes = [
        method["code"]
        for method in admin_methods
    ]

    assert "active_delivery_test" in admin_codes
    assert "inactive_delivery_test" in admin_codes


def test_duplicate_delivery_method_code_is_rejected(admin_headers):
    first_response = client.post(
        "/delivery-methods",
        json={
            "code": "duplicate_delivery_test",
            "name": "Duplicate Delivery",
            "price": 120,
            "active": True
        },
        headers=admin_headers
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/delivery-methods",
        json={
            "code": "duplicate_delivery_test",
            "name": "Another Delivery",
            "price": 500,
            "active": True
        },
        headers=admin_headers
    )

    assert second_response.status_code == 400
    assert (
        second_response.json()["detail"]
        == "Delivery method already exists"
    )


def test_admin_can_update_and_disable_delivery_method(admin_headers):
    create_response = client.post(
        "/delivery-methods",
        json={
            "code": "update_delivery_test",
            "name": "Old Delivery Name",
            "price": 100,
            "active": True
        },
        headers=admin_headers
    )

    assert create_response.status_code == 201

    delivery_method_id = create_response.json()["id"]

    update_response = client.patch(
        f"/delivery-methods/{delivery_method_id}",
        json={
            "name": "Updated Delivery Name",
            "price": 250,
            "active": False
        },
        headers=admin_headers
    )

    assert update_response.status_code == 200

    updated_method = update_response.json()

    assert updated_method["name"] == "Updated Delivery Name"
    assert updated_method["price"] == 250
    assert updated_method["active"] is False

    public_response = client.get(
        "/delivery-methods"
    )

    public_codes = [
        method["code"]
        for method in public_response.json()
    ]

    assert "update_delivery_test" not in public_codes

def test_order_with_delivery_method_adds_delivery_price(admin_headers):
    headers = create_test_user(
        "deliveryorderuser1",
        "deliveryorderuser1@example.com"
    )

    delivery_response = client.post(
        "/delivery-methods",
        json={
            "code": "order_standard_test",
            "name": "Order Standard Delivery",
            "price": 250,
            "active": True
        },
        headers=admin_headers
    )

    assert delivery_response.status_code == 201

    delivery_method_id = delivery_response.json()["id"]

    product_response = client.post(
        "/products",
        json={
            "name": "Delivery Order Product",
            "price": 2000,
            "in_stock": True,
            "stock_quantity": 5
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
        json={
            **SHIPPING_DATA,
            "delivery_method_id": delivery_method_id
        },
        headers=headers
    )

    assert response.status_code == 201

    order = response.json()

    assert order["delivery_method_id"] == delivery_method_id
    assert order["delivery_method_code"] == "order_standard_test"
    assert order["delivery_method_name"] == "Order Standard Delivery"
    assert order["delivery_price"] == 250

    # 2000 * 2 + 250 доставки
    assert order["total_price"] == 4250


def test_order_delivery_snapshot_does_not_change(admin_headers):
    headers = create_test_user(
        "deliveryorderuser2",
        "deliveryorderuser2@example.com"
    )

    delivery_response = client.post(
        "/delivery-methods",
        json={
            "code": "snapshot_delivery_test",
            "name": "Original Delivery",
            "price": 150,
            "active": True
        },
        headers=admin_headers
    )

    assert delivery_response.status_code == 201

    delivery_method_id = delivery_response.json()["id"]

    product_response = client.post(
        "/products",
        json={
            "name": "Snapshot Delivery Product",
            "price": 1000,
            "in_stock": True,
            "stock_quantity": 5
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
        json={
            **SHIPPING_DATA,
            "delivery_method_id": delivery_method_id
        },
        headers=headers
    )

    assert order_response.status_code == 201

    order_id = order_response.json()["id"]

    update_response = client.patch(
        f"/delivery-methods/{delivery_method_id}",
        json={
            "name": "Changed Delivery",
            "price": 500
        },
        headers=admin_headers
    )

    assert update_response.status_code == 200

    response = client.get(
        f"/orders/{order_id}",
        headers=headers
    )

    assert response.status_code == 200

    order = response.json()

    assert order["delivery_method_name"] == "Original Delivery"
    assert order["delivery_price"] == 150
    assert order["total_price"] == 1150


def test_inactive_delivery_method_cannot_be_used(admin_headers):
    headers = create_test_user(
        "deliveryorderuser3",
        "deliveryorderuser3@example.com"
    )

    delivery_response = client.post(
        "/delivery-methods",
        json={
            "code": "inactive_order_delivery_test",
            "name": "Inactive Order Delivery",
            "price": 300,
            "active": False
        },
        headers=admin_headers
    )

    assert delivery_response.status_code == 201

    delivery_method_id = delivery_response.json()["id"]

    product_response = client.post(
        "/products",
        json={
            "name": "Inactive Delivery Product",
            "price": 1200,
            "in_stock": True,
            "stock_quantity": 5
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

    response = client.post(
        "/orders",
        json={
            **SHIPPING_DATA,
            "delivery_method_id": delivery_method_id
        },
        headers=headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Delivery method not found"


def test_payment_includes_delivery_price(admin_headers):
    headers = create_test_user(
        "deliveryorderuser4",
        "deliveryorderuser4@example.com"
    )

    delivery_response = client.post(
        "/delivery-methods",
        json={
            "code": "payment_delivery_test",
            "name": "Payment Delivery",
            "price": 400,
            "active": True
        },
        headers=admin_headers
    )

    assert delivery_response.status_code == 201

    delivery_method_id = delivery_response.json()["id"]

    product_response = client.post(
        "/products",
        json={
            "name": "Payment Delivery Product",
            "price": 1600,
            "in_stock": True,
            "stock_quantity": 5
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
        json={
            **SHIPPING_DATA,
            "delivery_method_id": delivery_method_id
        },
        headers=headers
    )

    assert order_response.status_code == 201
    assert order_response.json()["total_price"] == 2000

    order_id = order_response.json()["id"]

    payment_response = client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    assert payment_response.status_code == 201
    assert payment_response.json()["amount"] == 2000

def test_order_saves_customer_note():
    headers = create_test_user(
        "noteuser1",
        "noteuser1@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Customer Note Product",
            "price": 1000,
            "in_stock": True,
            "stock_quantity": 5
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

    response = client.post(
        "/orders",
        json={
            **SHIPPING_DATA,
            "customer_note": "Call before delivery"
        },
        headers=headers
    )

    assert response.status_code == 201
    assert response.json()["customer_note"] == "Call before delivery"


def test_customer_note_cannot_exceed_500_characters():
    headers = create_test_user(
        "noteuser2",
        "noteuser2@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Long Note Product",
            "price": 1200,
            "in_stock": True,
            "stock_quantity": 5
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

    response = client.post(
        "/orders",
        json={
            **SHIPPING_DATA,
            "customer_note": "a" * 501
        },
        headers=headers
    )

    assert response.status_code == 422

def test_order_totals_without_discount_or_delivery():
    headers = create_test_user(
        "totalsuser1",
        "totalsuser1@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Totals Product 1",
            "price": 1500,
            "in_stock": True,
            "stock_quantity": 5
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

    assert order["subtotal"] == 3000
    assert order["discount_percent"] == 0
    assert order["discount_amount"] == 0
    assert order["delivery_price"] == 0
    assert order["total_price"] == 3000


def test_order_totals_with_discount_and_delivery(admin_headers):
    headers = create_test_user(
        "totalsuser2",
        "totalsuser2@example.com"
    )

    promo_response = client.post(
        "/promo-codes",
        json={
            "code": "TOTALS10",
            "discount_percent": 10,
            "active": True
        },
        headers=admin_headers
    )

    assert promo_response.status_code == 201

    delivery_response = client.post(
        "/delivery-methods",
        json={
            "code": "totals_delivery",
            "name": "Totals Delivery",
            "price": 250,
            "active": True
        },
        headers=admin_headers
    )

    assert delivery_response.status_code == 201

    delivery_method_id = delivery_response.json()["id"]

    product_response = client.post(
        "/products",
        json={
            "name": "Totals Product 2",
            "price": 2000,
            "in_stock": True,
            "stock_quantity": 5
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
        json={
            **SHIPPING_DATA,
            "promo_code": "TOTALS10",
            "delivery_method_id": delivery_method_id
        },
        headers=headers
    )

    assert response.status_code == 201

    order = response.json()

    assert order["subtotal"] == 4000
    assert order["discount_percent"] == 10
    assert order["discount_amount"] == 400
    assert order["delivery_price"] == 250
    assert order["total_price"] == 3850


def test_payment_uses_final_order_total(admin_headers):
    headers = create_test_user(
        "totalsuser3",
        "totalsuser3@example.com"
    )

    promo_response = client.post(
        "/promo-codes",
        json={
            "code": "PAYTOTAL10",
            "discount_percent": 10,
            "active": True
        },
        headers=admin_headers
    )

    assert promo_response.status_code == 201

    delivery_response = client.post(
        "/delivery-methods",
        json={
            "code": "payment_totals_delivery",
            "name": "Payment Totals Delivery",
            "price": 300,
            "active": True
        },
        headers=admin_headers
    )

    assert delivery_response.status_code == 201

    delivery_method_id = delivery_response.json()["id"]

    product_response = client.post(
        "/products",
        json={
            "name": "Totals Product 3",
            "price": 1000,
            "in_stock": True,
            "stock_quantity": 5
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

    order_response = client.post(
        "/orders",
        json={
            **SHIPPING_DATA,
            "promo_code": "PAYTOTAL10",
            "delivery_method_id": delivery_method_id
        },
        headers=headers
    )

    assert order_response.status_code == 201

    order = order_response.json()

    assert order["subtotal"] == 2000
    assert order["discount_amount"] == 200
    assert order["delivery_price"] == 300
    assert order["total_price"] == 2100

    order_id = order["id"]

    payment_response = client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    assert payment_response.status_code == 201
    assert payment_response.json()["amount"] == 2100

def test_order_item_line_total():
    headers = create_test_user(
        "linetotaluser1",
        "linetotaluser1@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Line Total Product",
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
            "quantity": 3
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

    assert len(order["items"]) == 1

    item = order["items"][0]

    assert item["price"] == 1500
    assert item["quantity"] == 3
    assert item["line_total"] == 4500

def test_admin_can_add_tracking_to_shipped_order(admin_headers):
    headers = create_test_user(
        "trackinguser1",
        "trackinguser1@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Tracking Product 1",
            "price": 1500,
            "in_stock": True,
            "stock_quantity": 5
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

    payment_response = client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    assert payment_response.status_code == 201

    shipped_response = client.patch(
        f"/admin/orders/{order_id}/status",
        json={
            "status": "shipped"
        },
        headers=admin_headers
    )

    assert shipped_response.status_code == 200

    response = client.patch(
        f"/admin/orders/{order_id}/tracking",
        json={
            "shipping_carrier": "Nova Poshta",
            "tracking_number": "20450000000000"
        },
        headers=admin_headers
    )

    assert response.status_code == 200

    order = response.json()

    assert order["shipping_carrier"] == "Nova Poshta"
    assert order["tracking_number"] == "20450000000000"


def test_tracking_cannot_be_added_to_pending_order(admin_headers):
    headers = create_test_user(
        "trackinguser2",
        "trackinguser2@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Tracking Product 2",
            "price": 1000,
            "in_stock": True,
            "stock_quantity": 5
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
        f"/admin/orders/{order_id}/tracking",
        json={
            "shipping_carrier": "Nova Poshta",
            "tracking_number": "TRACK-PENDING-001"
        },
        headers=admin_headers
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Tracking can only be added to shipped orders"
    )


def test_user_cannot_add_order_tracking():
    headers = create_test_user(
        "trackinguser3",
        "trackinguser3@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Tracking Product 3",
            "price": 1300,
            "in_stock": True,
            "stock_quantity": 5
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
        f"/admin/orders/{order_id}/tracking",
        json={
            "shipping_carrier": "Nova Poshta",
            "tracking_number": "TRACK-FORBIDDEN-001"
        },
        headers=headers
    )

    assert response.status_code == 403

def test_tracking_history_records_first_tracking_update(admin_headers):
    headers = create_test_user(
        "trackinghistoryuser1",
        "trackinghistoryuser1@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Tracking History Product 1",
            "price": 1400,
            "in_stock": True,
            "stock_quantity": 5
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

    client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    client.patch(
        f"/admin/orders/{order_id}/status",
        json={"status": "shipped"},
        headers=admin_headers
    )

    tracking_response = client.patch(
        f"/admin/orders/{order_id}/tracking",
        json={
            "shipping_carrier": "Nova Poshta",
            "tracking_number": "TRACK-HISTORY-001"
        },
        headers=admin_headers
    )

    assert tracking_response.status_code == 200

    history_response = client.get(
        f"/orders/{order_id}/tracking-history",
        headers=headers
    )

    assert history_response.status_code == 200

    history = history_response.json()

    assert len(history) == 1
    assert history[0]["order_id"] == order_id
    assert history[0]["shipping_carrier"] == "Nova Poshta"
    assert history[0]["tracking_number"] == "TRACK-HISTORY-001"
    assert "created_at" in history[0]


def test_tracking_history_records_tracking_replacement(admin_headers):
    headers = create_test_user(
        "trackinghistoryuser2",
        "trackinghistoryuser2@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Tracking History Product 2",
            "price": 1600,
            "in_stock": True,
            "stock_quantity": 5
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

    client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    client.patch(
        f"/admin/orders/{order_id}/status",
        json={"status": "shipped"},
        headers=admin_headers
    )

    first_response = client.patch(
        f"/admin/orders/{order_id}/tracking",
        json={
            "shipping_carrier": "Nova Poshta",
            "tracking_number": "TRACK-HISTORY-OLD"
        },
        headers=admin_headers
    )

    assert first_response.status_code == 200

    second_response = client.patch(
        f"/admin/orders/{order_id}/tracking",
        json={
            "shipping_carrier": "Ukrposhta",
            "tracking_number": "TRACK-HISTORY-NEW"
        },
        headers=admin_headers
    )

    assert second_response.status_code == 200
    assert second_response.json()["shipping_carrier"] == "Ukrposhta"
    assert second_response.json()["tracking_number"] == "TRACK-HISTORY-NEW"

    history_response = client.get(
        f"/orders/{order_id}/tracking-history",
        headers=headers
    )

    assert history_response.status_code == 200

    history = history_response.json()

    assert len(history) == 2

    assert history[0]["shipping_carrier"] == "Nova Poshta"
    assert history[0]["tracking_number"] == "TRACK-HISTORY-OLD"

    assert history[1]["shipping_carrier"] == "Ukrposhta"
    assert history[1]["tracking_number"] == "TRACK-HISTORY-NEW"


def test_user_cannot_view_another_users_tracking_history(admin_headers):
    owner_headers = create_test_user(
        "trackinghistoryowner",
        "trackinghistoryowner@example.com"
    )

    other_headers = create_test_user(
        "trackinghistoryother",
        "trackinghistoryother@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Tracking History Private Product",
            "price": 1800,
            "in_stock": True,
            "stock_quantity": 5
        },
        headers=owner_headers
    )

    product_id = product_response.json()["id"]

    client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 1
        },
        headers=owner_headers
    )

    order_response = client.post(
        "/orders",
        json=SHIPPING_DATA,
        headers=owner_headers
    )

    order_id = order_response.json()["id"]

    client.post(
        f"/orders/{order_id}/pay",
        headers=owner_headers
    )

    client.patch(
        f"/admin/orders/{order_id}/status",
        json={"status": "shipped"},
        headers=admin_headers
    )

    client.patch(
        f"/admin/orders/{order_id}/tracking",
        json={
            "shipping_carrier": "Nova Poshta",
            "tracking_number": "TRACK-PRIVATE-001"
        },
        headers=admin_headers
    )

    response = client.get(
        f"/orders/{order_id}/tracking-history",
        headers=other_headers
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"

def test_admin_can_set_estimated_delivery_date_for_shipped_order(
    admin_headers
):
    headers = create_test_user(
        "estimateddateuser1",
        "estimateddateuser1@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Estimated Date Product 1",
            "price": 1500,
            "in_stock": True,
            "stock_quantity": 5
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

    assert order_response.status_code == 201

    order_id = order_response.json()["id"]

    payment_response = client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    assert payment_response.status_code == 201

    shipped_response = client.patch(
        f"/admin/orders/{order_id}/status",
        json={
            "status": "shipped"
        },
        headers=admin_headers
    )

    assert shipped_response.status_code == 200

    response = client.patch(
        f"/admin/orders/{order_id}/estimated-delivery",
        json={
            "estimated_delivery_date": "2099-12-31"
        },
        headers=admin_headers
    )

    assert response.status_code == 200
    assert (
        response.json()["estimated_delivery_date"]
        == "2099-12-31"
    )


def test_estimated_delivery_date_cannot_be_in_past(
    admin_headers
):
    headers = create_test_user(
        "estimateddateuser2",
        "estimateddateuser2@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Estimated Date Product 2",
            "price": 1200,
            "in_stock": True,
            "stock_quantity": 5
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

    payment_response = client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    assert payment_response.status_code == 201

    shipped_response = client.patch(
        f"/admin/orders/{order_id}/status",
        json={
            "status": "shipped"
        },
        headers=admin_headers
    )

    assert shipped_response.status_code == 200

    response = client.patch(
        f"/admin/orders/{order_id}/estimated-delivery",
        json={
            "estimated_delivery_date": "2000-01-01"
        },
        headers=admin_headers
    )

    assert response.status_code == 422


def test_user_cannot_set_estimated_delivery_date():
    headers = create_test_user(
        "estimateddateuser3",
        "estimateddateuser3@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Estimated Date Product 3",
            "price": 1000,
            "in_stock": True,
            "stock_quantity": 5
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
        f"/admin/orders/{order_id}/estimated-delivery",
        json={
            "estimated_delivery_date": "2099-12-31"
        },
        headers=headers
    )

    assert response.status_code == 403

def test_shipment_events_full_history(admin_headers):
    headers = create_test_user(
        "shipmenteventuser1",
        "shipmenteventuser1@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Shipment Event Product 1",
            "price": 1500,
            "in_stock": True,
            "stock_quantity": 5
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

    assert order_response.status_code == 201

    order_id = order_response.json()["id"]

    payment_response = client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    assert payment_response.status_code == 201

    shipped_response = client.patch(
        f"/admin/orders/{order_id}/status",
        json={
            "status": "shipped"
        },
        headers=admin_headers
    )

    assert shipped_response.status_code == 200

    events = [
        {
            "status": "picked_up",
            "comment": "Package picked up"
        },
        {
            "status": "in_transit",
            "comment": "Package is in transit"
        },
        {
            "status": "out_for_delivery",
            "comment": "Courier is delivering package"
        },
        {
            "status": "delivered",
            "comment": "Package delivered"
        },
    ]

    for event in events:
        response = client.post(
            f"/admin/orders/{order_id}/shipment-events",
            json=event,
            headers=admin_headers
        )

        assert response.status_code == 201

    response = client.get(
        f"/orders/{order_id}/shipment-events",
        headers=headers
    )

    assert response.status_code == 200

    history = response.json()

    assert len(history) == 4

    assert history[0]["status"] == "picked_up"
    assert history[1]["status"] == "in_transit"
    assert history[2]["status"] == "out_for_delivery"
    assert history[3]["status"] == "delivered"


def test_user_cannot_create_shipment_event():
    headers = create_test_user(
        "shipmenteventuser2",
        "shipmenteventuser2@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Shipment Event Product 2",
            "price": 1000,
            "in_stock": True,
            "stock_quantity": 5
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

    response = client.post(
        f"/admin/orders/{order_id}/shipment-events",
        json={
            "status": "picked_up",
            "comment": "Should be forbidden"
        },
        headers=headers
    )

    assert response.status_code == 403


def test_shipment_event_cannot_be_added_to_pending_order(
    admin_headers
):
    headers = create_test_user(
        "shipmenteventuser3",
        "shipmenteventuser3@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Shipment Event Product 3",
            "price": 1200,
            "in_stock": True,
            "stock_quantity": 5
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

    response = client.post(
        f"/admin/orders/{order_id}/shipment-events",
        json={
            "status": "picked_up",
            "comment": "Too early"
        },
        headers=admin_headers
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Shipment events can only be added to shipped orders"
    )
def test_user_cannot_view_another_users_shipment_events(
    admin_headers
):
    headers1 = create_test_user(
        "shipmenteventuser4",
        "shipmenteventuser4@example.com"
    )

    headers2 = create_test_user(
        "shipmenteventuser5",
        "shipmenteventuser5@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Shipment Event Product 4",
            "price": 1400,
            "in_stock": True,
            "stock_quantity": 5
        },
        headers=headers1
    )

    product_id = product_response.json()["id"]

    client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 1
        },
        headers=headers1
    )

    order_response = client.post(
        "/orders",
        json=SHIPPING_DATA,
        headers=headers1
    )

    assert order_response.status_code == 201

    order_id = order_response.json()["id"]

    client.post(
        f"/orders/{order_id}/pay",
        headers=headers1
    )

    client.patch(
        f"/admin/orders/{order_id}/status",
        json={
            "status": "shipped"
        },
        headers=admin_headers
    )

    event_response = client.post(
        f"/admin/orders/{order_id}/shipment-events",
        json={
            "status": "picked_up",
            "comment": "Package picked up"
        },
        headers=admin_headers
    )

    assert event_response.status_code == 201

    response = client.get(
        f"/orders/{order_id}/shipment-events",
        headers=headers2
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"

def advance_shipment_to_out_for_delivery(
    order_id: int,
    admin_headers
):
    statuses = [
        "picked_up",
        "in_transit",
        "out_for_delivery",
    ]

    for status in statuses:
        response = client.post(
            f"/admin/orders/{order_id}/shipment-events",
            json={
                "status": status,
                "comment": f"Shipment status: {status}"
            },
            headers=admin_headers
        )

        assert response.status_code == 201

def advance_shipment_to_out_for_delivery(
    order_id: int,
    admin_headers
):
    statuses = [
        "picked_up",
        "in_transit",
        "out_for_delivery",
    ]

    for status in statuses:
        response = client.post(
            f"/admin/orders/{order_id}/shipment-events",
            json={
                "status": status,
                "comment": f"Shipment status: {status}"
            },
            headers=admin_headers
        )

        assert response.status_code == 201

def test_delivered_shipment_event_completes_order(
    admin_headers
):
    headers = create_test_user(
        "shipmentcompleteuser1",
        "shipmentcompleteuser1@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Shipment Complete Product",
            "price": 1700,
            "in_stock": True,
            "stock_quantity": 5
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

    assert order_response.status_code == 201

    order_id = order_response.json()["id"]

    payment_response = client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    assert payment_response.status_code == 201

    shipped_response = client.patch(
    f"/admin/orders/{order_id}/status",
    json={
        "status": "shipped"
    },
    headers=admin_headers
)

    assert shipped_response.status_code == 200

    advance_shipment_to_out_for_delivery(
        order_id,
        admin_headers
    )

    delivered_response = client.post(
        f"/admin/orders/{order_id}/shipment-events",
        json={
            "status": "delivered",
            "comment": "Package delivered successfully"
        },
        headers=admin_headers
    )

    assert delivered_response.status_code == 201
    assert delivered_response.json()["status"] == "delivered"

    order_response = client.get(
        f"/orders/{order_id}",
        headers=headers
)

    assert order_response.status_code == 200

    order = order_response.json()

    assert order["status"] == "completed"
    assert order["delivered_at"] is not None

    history_response = client.get(
        f"/orders/{order_id}/status-history",
        headers=headers
    )

    assert history_response.status_code == 200

    history = history_response.json()

    assert history[-1]["old_status"] == "shipped"
    assert history[-1]["new_status"] == "completed"

def test_delivered_shipment_event_cannot_be_added_twice(
    admin_headers
):
    headers = create_test_user(
        "shipmentcompleteuser2",
        "shipmentcompleteuser2@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Double Delivered Product",
            "price": 1800,
            "in_stock": True,
            "stock_quantity": 5
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

    client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    client.patch(
        f"/admin/orders/{order_id}/status",
        json={
            "status": "shipped"
        },
        headers=admin_headers
    )
    advance_shipment_to_out_for_delivery(
    order_id,
    admin_headers
)

    first_response = client.post(
        f"/admin/orders/{order_id}/shipment-events",
        json={
            "status": "delivered",
            "comment": "Delivered"
        },
        headers=admin_headers
    )

    assert first_response.status_code == 201

    second_response = client.post(
        f"/admin/orders/{order_id}/shipment-events",
        json={
            "status": "delivered",
            "comment": "Delivered again"
        },
        headers=admin_headers
    )

    assert second_response.status_code == 400
    assert (
        second_response.json()["detail"]
        == "Shipment events can only be added to shipped orders"
    )


def test_shipment_event_cannot_be_added_after_delivery(
    admin_headers
):
    headers = create_test_user(
        "shipmentcompleteuser3",
        "shipmentcompleteuser3@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "After Delivery Product",
            "price": 1600,
            "in_stock": True,
            "stock_quantity": 5
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

    client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    client.patch(
        f"/admin/orders/{order_id}/status",
        json={
            "status": "shipped"
        },
        headers=admin_headers
    )
    advance_shipment_to_out_for_delivery(
    order_id,
    admin_headers
)

    delivered_response = client.post(
        f"/admin/orders/{order_id}/shipment-events",
        json={
            "status": "delivered",
            "comment": "Delivered successfully"
        },
        headers=admin_headers
    )

    assert delivered_response.status_code == 201

    response = client.post(
        f"/admin/orders/{order_id}/shipment-events",
        json={
            "status": "in_transit",
            "comment": "Invalid event after delivery"
        },
        headers=admin_headers
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Shipment events can only be added to shipped orders"
    )

def test_first_shipment_event_must_be_picked_up(admin_headers):
    headers = create_test_user(
        "shipmenttransitionuser1",
        "shipmenttransitionuser1@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Shipment Transition Product 1",
            "price": 1500,
            "in_stock": True,
            "stock_quantity": 5
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

    client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    client.patch(
        f"/admin/orders/{order_id}/status",
        json={"status": "shipped"},
        headers=admin_headers
    )

    response = client.post(
        f"/admin/orders/{order_id}/shipment-events",
        json={
            "status": "in_transit",
            "comment": "Invalid first event"
        },
        headers=admin_headers
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Invalid shipment status transition"
    )


def test_shipment_event_cannot_skip_status(admin_headers):
    headers = create_test_user(
        "shipmenttransitionuser2",
        "shipmenttransitionuser2@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Shipment Transition Product 2",
            "price": 1600,
            "in_stock": True,
            "stock_quantity": 5
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

    client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    client.patch(
        f"/admin/orders/{order_id}/status",
        json={"status": "shipped"},
        headers=admin_headers
    )

    first_response = client.post(
        f"/admin/orders/{order_id}/shipment-events",
        json={
            "status": "picked_up",
            "comment": "Picked up"
        },
        headers=admin_headers
    )

    assert first_response.status_code == 201

    response = client.post(
        f"/admin/orders/{order_id}/shipment-events",
        json={
            "status": "out_for_delivery",
            "comment": "Skipped in_transit"
        },
        headers=admin_headers
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Invalid shipment status transition"
    )


def test_shipment_event_cannot_go_backwards(admin_headers):
    headers = create_test_user(
        "shipmenttransitionuser3",
        "shipmenttransitionuser3@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Shipment Transition Product 3",
            "price": 1700,
            "in_stock": True,
            "stock_quantity": 5
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

    client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    client.patch(
        f"/admin/orders/{order_id}/status",
        json={"status": "shipped"},
        headers=admin_headers
    )

    first_response = client.post(
        f"/admin/orders/{order_id}/shipment-events",
        json={
            "status": "picked_up",
            "comment": "Picked up"
        },
        headers=admin_headers
    )

    assert first_response.status_code == 201

    second_response = client.post(
        f"/admin/orders/{order_id}/shipment-events",
        json={
            "status": "in_transit",
            "comment": "In transit"
        },
        headers=admin_headers
    )

    assert second_response.status_code == 201

    response = client.post(
        f"/admin/orders/{order_id}/shipment-events",
        json={
            "status": "picked_up",
            "comment": "Trying to go backwards"
        },
        headers=admin_headers
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Invalid shipment status transition"
    )

def test_admin_can_view_store_stats(admin_headers):
    response = client.get(
        "/admin/stats",
        headers=admin_headers
    )

    assert response.status_code == 200

    stats = response.json()

    assert "total_users" in stats
    assert "total_products" in stats
    assert "total_orders" in stats
    assert "completed_orders" in stats
    assert "total_revenue" in stats

    assert isinstance(stats["total_users"], int)
    assert isinstance(stats["total_products"], int)
    assert isinstance(stats["total_orders"], int)
    assert isinstance(stats["completed_orders"], int)
    assert isinstance(stats["total_revenue"], int)


def test_regular_user_cannot_view_store_stats():
    headers = create_test_user(
        "adminstatsuser1",
        "adminstatsuser1@example.com"
    )

    response = client.get(
        "/admin/stats",
        headers=headers
    )

    assert response.status_code == 403


def test_admin_stats_revenue_counts_only_completed_orders(
    admin_headers
):
    initial_response = client.get(
        "/admin/stats",
        headers=admin_headers
    )

    assert initial_response.status_code == 200

    initial_stats = initial_response.json()

    headers = create_test_user(
        "adminstatsuser2",
        "adminstatsuser2@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Admin Stats Product",
            "price": 2500,
            "in_stock": True,
            "stock_quantity": 5
        },
        headers=headers
    )

    assert product_response.status_code == 201

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

    assert order_response.status_code == 201

    order = order_response.json()
    order_id = order["id"]
    order_total = order["total_price"]

    pending_stats_response = client.get(
        "/admin/stats",
        headers=admin_headers
    )

    assert pending_stats_response.status_code == 200

    pending_stats = pending_stats_response.json()

    assert (
        pending_stats["total_orders"]
        == initial_stats["total_orders"] + 1
    )

    assert (
        pending_stats["total_revenue"]
        == initial_stats["total_revenue"]
    )

    payment_response = client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    assert payment_response.status_code == 201

    shipped_response = client.patch(
        f"/admin/orders/{order_id}/status",
        json={
            "status": "shipped"
        },
        headers=admin_headers
    )

    assert shipped_response.status_code == 200

    advance_shipment_to_out_for_delivery(
        order_id,
        admin_headers
    )

    delivered_response = client.post(
        f"/admin/orders/{order_id}/shipment-events",
        json={
            "status": "delivered",
            "comment": "Delivered for admin stats test"
        },
        headers=admin_headers
    )

    assert delivered_response.status_code == 201

    final_response = client.get(
        "/admin/stats",
        headers=admin_headers
    )

    assert final_response.status_code == 200

    final_stats = final_response.json()

    assert (
        final_stats["completed_orders"]
        == initial_stats["completed_orders"] + 1
    )

    assert (
        final_stats["total_revenue"]
        == initial_stats["total_revenue"] + order_total
    )

def test_admin_can_view_top_products(admin_headers):
    response = client.get(
        "/admin/stats/top-products",
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_regular_user_cannot_view_top_products():
    headers = create_test_user(
        "topproductsuser1",
        "topproductsuser1@example.com"
    )

    response = client.get(
        "/admin/stats/top-products",
        headers=headers
    )

    assert response.status_code == 403


def test_top_products_are_sorted_by_units_sold_and_limited(
    admin_headers
):
    headers = create_test_user(
        "topproductsuser2",
        "topproductsuser2@example.com"
    )

    product1_response = client.post(
        "/products",
        json={
            "name": "Top Product A",
            "price": 1000,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    product2_response = client.post(
        "/products",
        json={
            "name": "Top Product B",
            "price": 2000,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    product1_id = product1_response.json()["id"]
    product2_id = product2_response.json()["id"]

    client.post(
        "/cart",
        json={
            "product_id": product1_id,
            "quantity": 3
        },
        headers=headers
    )

    order1_response = client.post(
        "/orders",
        json=SHIPPING_DATA,
        headers=headers
    )

    order1_id = order1_response.json()["id"]

    client.post(
        f"/orders/{order1_id}/pay",
        headers=headers
    )

    client.patch(
        f"/admin/orders/{order1_id}/status",
        json={"status": "shipped"},
        headers=admin_headers
    )

    advance_shipment_to_out_for_delivery(
        order1_id,
        admin_headers
    )

    client.post(
        f"/admin/orders/{order1_id}/shipment-events",
        json={
            "status": "delivered",
            "comment": "Delivered"
        },
        headers=admin_headers
    )

    client.post(
        "/cart",
        json={
            "product_id": product2_id,
            "quantity": 1
        },
        headers=headers
    )

    order2_response = client.post(
        "/orders",
        json=SHIPPING_DATA,
        headers=headers
    )

    order2_id = order2_response.json()["id"]

    client.post(
        f"/orders/{order2_id}/pay",
        headers=headers
    )

    client.patch(
        f"/admin/orders/{order2_id}/status",
        json={"status": "shipped"},
        headers=admin_headers
    )

    advance_shipment_to_out_for_delivery(
        order2_id,
        admin_headers
    )

    client.post(
        f"/admin/orders/{order2_id}/shipment-events",
        json={
            "status": "delivered",
            "comment": "Delivered"
        },
        headers=admin_headers
    )

    response = client.get(
        "/admin/stats/top-products?limit=1",
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["product_id"] == product1_id
    assert data[0]["product_name"] == "Top Product A"
    assert data[0]["units_sold"] == 3
    assert data[0]["revenue"] == 3000

def test_admin_can_view_sales_by_day(admin_headers):
    response = client.get(
        "/admin/stats/sales-by-day?days=7",
        headers=admin_headers
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_regular_user_cannot_view_sales_by_day():
    headers = create_test_user(
        "salesbydayuser1",
        "salesbydayuser1@example.com"
    )

    response = client.get(
        "/admin/stats/sales-by-day?days=7",
        headers=headers
    )

    assert response.status_code == 403


def test_sales_by_day_counts_completed_order(
    admin_headers
):
    initial_response = client.get(
        "/admin/stats/sales-by-day?days=1",
        headers=admin_headers
    )

    assert initial_response.status_code == 200

    initial_data = initial_response.json()

    initial_orders = sum(
        item["orders"]
        for item in initial_data
    )

    initial_revenue = sum(
        item["revenue"]
        for item in initial_data
    )

    headers = create_test_user(
        "salesbydayuser2",
        "salesbydayuser2@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Daily Sales Product",
            "price": 2300,
            "in_stock": True,
            "stock_quantity": 5
        },
        headers=headers
    )

    assert product_response.status_code == 201

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

    assert order_response.status_code == 201

    order = order_response.json()
    order_id = order["id"]
    order_total = order["total_price"]

    client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    shipped_response = client.patch(
        f"/admin/orders/{order_id}/status",
        json={
            "status": "shipped"
        },
        headers=admin_headers
    )

    assert shipped_response.status_code == 200

    advance_shipment_to_out_for_delivery(
        order_id,
        admin_headers
    )

    delivered_response = client.post(
        f"/admin/orders/{order_id}/shipment-events",
        json={
            "status": "delivered",
            "comment": "Delivered for daily sales"
        },
        headers=admin_headers
    )

    assert delivered_response.status_code == 201

    final_response = client.get(
        "/admin/stats/sales-by-day?days=1",
        headers=admin_headers
    )

    assert final_response.status_code == 200

    final_data = final_response.json()

    final_orders = sum(
        item["orders"]
        for item in final_data
    )

    final_revenue = sum(
        item["revenue"]
        for item in final_data
    )

    assert final_orders == initial_orders + 1
    assert final_revenue == initial_revenue + order_total

def test_admin_can_view_orders_by_status(admin_headers):
    response = client.get(
        "/admin/stats/orders-by-status",
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    for item in data:
        assert "status" in item
        assert "orders" in item
        assert isinstance(item["orders"], int)


def test_regular_user_cannot_view_orders_by_status():
    headers = create_test_user(
        "ordersbystatususer1",
        "ordersbystatususer1@example.com"
    )

    response = client.get(
        "/admin/stats/orders-by-status",
        headers=headers
    )

    assert response.status_code == 403


def test_orders_by_status_pending_count_increases(
    admin_headers
):
    initial_response = client.get(
        "/admin/stats/orders-by-status",
        headers=admin_headers
    )

    assert initial_response.status_code == 200

    initial_data = initial_response.json()

    initial_pending = next(
        (
            item["orders"]
            for item in initial_data
            if item["status"] == "pending"
        ),
        0
    )

    headers = create_test_user(
        "ordersbystatususer2",
        "ordersbystatususer2@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Orders By Status Product",
            "price": 1900,
            "in_stock": True,
            "stock_quantity": 5
        },
        headers=headers
    )

    assert product_response.status_code == 201

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

    assert order_response.status_code == 201
    assert order_response.json()["status"] == "pending"

    final_response = client.get(
        "/admin/stats/orders-by-status",
        headers=admin_headers
    )

    assert final_response.status_code == 200

    final_data = final_response.json()

    final_pending = next(
        item["orders"]
        for item in final_data
        if item["status"] == "pending"
    )

    assert final_pending == initial_pending + 1

def test_admin_can_view_low_stock_products(admin_headers):
    response = client.get(
        "/admin/inventory/low-stock?threshold=5",
        headers=admin_headers
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_regular_user_cannot_view_low_stock_products():
    headers = create_test_user(
        "lowstockuser1",
        "lowstockuser1@example.com"
    )

    response = client.get(
        "/admin/inventory/low-stock?threshold=5",
        headers=headers
    )

    assert response.status_code == 403


def test_low_stock_products_are_filtered_and_sorted(
    admin_headers
):
    headers = create_test_user(
        "lowstockuser2",
        "lowstockuser2@example.com"
    )

    product1_response = client.post(
        "/products",
        json={
            "name": "Low Stock Product A",
            "price": 1000,
            "in_stock": True,
            "stock_quantity": 2
        },
        headers=headers
    )

    product2_response = client.post(
        "/products",
        json={
            "name": "Low Stock Product B",
            "price": 1200,
            "in_stock": True,
            "stock_quantity": 4
        },
        headers=headers
    )

    product3_response = client.post(
        "/products",
        json={
            "name": "Enough Stock Product",
            "price": 1400,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    product1_id = product1_response.json()["id"]
    product2_id = product2_response.json()["id"]
    product3_id = product3_response.json()["id"]

    response = client.get(
        "/admin/inventory/low-stock?threshold=5",
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()

    ids = [item["product_id"] for item in data]

    assert product1_id in ids
    assert product2_id in ids
    assert product3_id not in ids

    filtered = [
        item
        for item in data
        if item["product_id"] in {product1_id, product2_id}
    ]

    assert len(filtered) == 2
    assert filtered[0]["stock_quantity"] == 2
    assert filtered[1]["stock_quantity"] == 4

def test_stock_movement_created_when_order_is_created(
    admin_headers
):
    headers = create_test_user(
        "stockmovementuser1",
        "stockmovementuser1@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Stock Movement Product 1",
            "price": 1500,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    assert product_response.status_code == 201

    product_id = product_response.json()["id"]

    client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 3
        },
        headers=headers
    )

    order_response = client.post(
        "/orders",
        json=SHIPPING_DATA,
        headers=headers
    )

    assert order_response.status_code == 201

    history_response = client.get(
        f"/products/{product_id}/stock-movements",
        headers=admin_headers
    )

    assert history_response.status_code == 200

    history = history_response.json()

    assert len(history) == 1
    assert history[0]["product_id"] == product_id
    assert history[0]["quantity_change"] == -3
    assert history[0]["reason"] == "order"


def test_stock_movement_created_when_order_is_cancelled(
    admin_headers
):
    headers = create_test_user(
        "stockmovementuser2",
        "stockmovementuser2@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Stock Movement Product 2",
            "price": 1600,
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

    order_response = client.post(
        "/orders",
        json=SHIPPING_DATA,
        headers=headers
    )

    assert order_response.status_code == 201

    order_id = order_response.json()["id"]

    cancel_response = client.post(
        f"/orders/{order_id}/cancel",
        headers=headers
    )

    assert cancel_response.status_code == 200

    history_response = client.get(
        f"/products/{product_id}/stock-movements",
        headers=admin_headers
    )

    assert history_response.status_code == 200

    history = history_response.json()

    assert len(history) == 2

    assert history[0]["quantity_change"] == -2
    assert history[0]["reason"] == "order"

    assert history[1]["quantity_change"] == 2
    assert history[1]["reason"] == "cancellation"


def test_stock_movement_created_when_order_is_refunded(
    admin_headers
):
    headers = create_test_user(
        "stockmovementuser3",
        "stockmovementuser3@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Stock Movement Product 3",
            "price": 1700,
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
            "quantity": 4
        },
        headers=headers
    )

    order_response = client.post(
        "/orders",
        json=SHIPPING_DATA,
        headers=headers
    )

    assert order_response.status_code == 201

    order_id = order_response.json()["id"]

    payment_response = client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    assert payment_response.status_code == 201

    refund_response = client.post(
        f"/orders/{order_id}/refund",
        headers=headers
    )

    assert refund_response.status_code == 200

    history_response = client.get(
        f"/products/{product_id}/stock-movements",
        headers=admin_headers
    )

    assert history_response.status_code == 200

    history = history_response.json()

    assert len(history) == 2

    assert history[0]["quantity_change"] == -4
    assert history[0]["reason"] == "order"

    assert history[1]["quantity_change"] == 4
    assert history[1]["reason"] == "refund"


def test_regular_user_cannot_view_stock_movements():
    headers = create_test_user(
        "stockmovementuser4",
        "stockmovementuser4@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Stock Movement Product 4",
            "price": 1800,
            "in_stock": True,
            "stock_quantity": 5
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    response = client.get(
        f"/products/{product_id}/stock-movements",
        headers=headers
    )

    assert response.status_code == 403

def test_admin_can_restock_product(admin_headers):
    headers = create_test_user(
        "restockuser1",
        "restockuser1@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Restock Product 1",
            "price": 1500,
            "in_stock": True,
            "stock_quantity": 2
        },
        headers=headers
    )

    assert product_response.status_code == 201

    product_id = product_response.json()["id"]

    response = client.post(
        f"/products/{product_id}/restock",
        json={
            "quantity": 5
        },
        headers=admin_headers
    )

    assert response.status_code == 200

    product = response.json()

    assert product["stock_quantity"] == 7
    assert product["in_stock"] is True


def test_regular_user_cannot_restock_product():
    headers = create_test_user(
        "restockuser2",
        "restockuser2@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Restock Product 2",
            "price": 1600,
            "in_stock": True,
            "stock_quantity": 3
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    response = client.post(
        f"/products/{product_id}/restock",
        json={
            "quantity": 5
        },
        headers=headers
    )

    assert response.status_code == 403


def test_restock_quantity_must_be_positive(admin_headers):
    headers = create_test_user(
        "restockuser3",
        "restockuser3@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Restock Product 3",
            "price": 1700,
            "in_stock": True,
            "stock_quantity": 4
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    response = client.post(
        f"/products/{product_id}/restock",
        json={
            "quantity": 0
        },
        headers=admin_headers
    )

    assert response.status_code == 422


def test_restock_creates_stock_movement(admin_headers):
    headers = create_test_user(
        "restockuser4",
        "restockuser4@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Restock Product 4",
            "price": 1800,
            "in_stock": True,
            "stock_quantity": 1
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    restock_response = client.post(
        f"/products/{product_id}/restock",
        json={
            "quantity": 6
        },
        headers=admin_headers
    )

    assert restock_response.status_code == 200

    history_response = client.get(
        f"/products/{product_id}/stock-movements",
        headers=admin_headers
    )

    assert history_response.status_code == 200

    history = history_response.json()

    assert len(history) == 1
    assert history[0]["quantity_change"] == 6
    assert history[0]["reason"] == "restock"

def test_admin_can_adjust_product_stock(admin_headers):
    headers = create_test_user(
        "stockadjustuser1",
        "stockadjustuser1@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Stock Adjustment Product 1",
            "price": 1500,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    assert product_response.status_code == 201

    product_id = product_response.json()["id"]

    decrease_response = client.post(
        f"/products/{product_id}/adjust-stock",
        json={
            "quantity_change": -3,
            "reason": "damaged"
        },
        headers=admin_headers
    )

    assert decrease_response.status_code == 200
    assert decrease_response.json()["stock_quantity"] == 7

    increase_response = client.post(
        f"/products/{product_id}/adjust-stock",
        json={
            "quantity_change": 2,
            "reason": "inventory correction"
        },
        headers=admin_headers
    )

    assert increase_response.status_code == 200
    assert increase_response.json()["stock_quantity"] == 9


def test_stock_adjustment_cannot_make_stock_negative(
    admin_headers
):
    headers = create_test_user(
        "stockadjustuser2",
        "stockadjustuser2@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Stock Adjustment Product 2",
            "price": 1600,
            "in_stock": True,
            "stock_quantity": 3
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    response = client.post(
        f"/products/{product_id}/adjust-stock",
        json={
            "quantity_change": -4,
            "reason": "damaged"
        },
        headers=admin_headers
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Stock quantity cannot be negative"
    )


def test_regular_user_cannot_adjust_product_stock():
    headers = create_test_user(
        "stockadjustuser3",
        "stockadjustuser3@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Stock Adjustment Product 3",
            "price": 1700,
            "in_stock": True,
            "stock_quantity": 5
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    response = client.post(
        f"/products/{product_id}/adjust-stock",
        json={
            "quantity_change": -1,
            "reason": "damaged"
        },
        headers=headers
    )

    assert response.status_code == 403


def test_stock_adjustment_creates_stock_movement(
    admin_headers
):
    headers = create_test_user(
        "stockadjustuser4",
        "stockadjustuser4@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Stock Adjustment Product 4",
            "price": 1800,
            "in_stock": True,
            "stock_quantity": 8
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    adjustment_response = client.post(
        f"/products/{product_id}/adjust-stock",
        json={
            "quantity_change": -2,
            "reason": "damaged"
        },
        headers=admin_headers
    )

    assert adjustment_response.status_code == 200

    history_response = client.get(
        f"/products/{product_id}/stock-movements",
        headers=admin_headers
    )

    assert history_response.status_code == 200

    history = history_response.json()

    assert len(history) == 1
    assert history[0]["quantity_change"] == -2
    assert history[0]["reason"] == "damaged"

def test_admin_can_view_inventory_summary(admin_headers):
    response = client.get(
        "/admin/inventory/summary",
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_products" in data
    assert "in_stock_products" in data
    assert "out_of_stock_products" in data
    assert "total_units" in data
    assert "inventory_value" in data


def test_regular_user_cannot_view_inventory_summary():
    headers = create_test_user(
        "inventorysummaryuser1",
        "inventorysummaryuser1@example.com"
    )

    response = client.get(
        "/admin/inventory/summary",
        headers=headers
    )

    assert response.status_code == 403


def test_inventory_summary_counts_products_units_and_value(
    admin_headers
):
    initial_response = client.get(
        "/admin/inventory/summary",
        headers=admin_headers
    )

    assert initial_response.status_code == 200

    initial = initial_response.json()

    headers = create_test_user(
        "inventorysummaryuser2",
        "inventorysummaryuser2@example.com"
    )

    product1_response = client.post(
        "/products",
        json={
            "name": "Inventory Summary Product 1",
            "price": 1000,
            "in_stock": True,
            "stock_quantity": 3
        },
        headers=headers
    )

    product2_response = client.post(
        "/products",
        json={
            "name": "Inventory Summary Product 2",
            "price": 2000,
            "in_stock": True,
            "stock_quantity": 2
        },
        headers=headers
    )

    product3_response = client.post(
        "/products",
        json={
            "name": "Inventory Summary Product 3",
            "price": 3000,
            "in_stock": False,
            "stock_quantity": 0
        },
        headers=headers
    )

    assert product1_response.status_code == 201
    assert product2_response.status_code == 201
    assert product3_response.status_code == 201

    final_response = client.get(
        "/admin/inventory/summary",
        headers=admin_headers
    )

    assert final_response.status_code == 200

    final = final_response.json()

    assert (
        final["total_products"]
        == initial["total_products"] + 3
    )

    assert (
        final["in_stock_products"]
        == initial["in_stock_products"] + 2
    )

    assert (
        final["out_of_stock_products"]
        == initial["out_of_stock_products"] + 1
    )

    assert (
        final["total_units"]
        == initial["total_units"] + 5
    )

    expected_added_value = (
        1000 * 3
        + 2000 * 2
    )

    assert (
        final["inventory_value"]
        == initial["inventory_value"] + expected_added_value
    )

def test_admin_can_view_all_stock_movements(admin_headers):
    response = client.get(
        "/admin/inventory/movements",
        headers=admin_headers
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_regular_user_cannot_view_all_stock_movements():
    headers = create_test_user(
        "inventorymovementuser1",
        "inventorymovementuser1@example.com"
    )

    response = client.get(
        "/admin/inventory/movements",
        headers=headers
    )

    assert response.status_code == 403


def test_stock_movements_can_be_filtered_by_product_and_reason(
    admin_headers
):
    headers = create_test_user(
        "inventorymovementuser2",
        "inventorymovementuser2@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Inventory Movement Product",
            "price": 1500,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    client.post(
        f"/products/{product_id}/restock",
        json={
            "quantity": 5
        },
        headers=admin_headers
    )

    client.post(
        f"/products/{product_id}/adjust-stock",
        json={
            "quantity_change": -2,
            "reason": "damaged"
        },
        headers=admin_headers
    )

    response = client.get(
        (
            "/admin/inventory/movements"
            f"?product_id={product_id}&reason=damaged"
        ),
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["product_id"] == product_id
    assert data[0]["quantity_change"] == -2
    assert data[0]["reason"] == "damaged"


def test_stock_movements_support_pagination(admin_headers):
    headers = create_test_user(
        "inventorymovementuser3",
        "inventorymovementuser3@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Inventory Pagination Product",
            "price": 1600,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    client.post(
        f"/products/{product_id}/restock",
        json={"quantity": 1},
        headers=admin_headers
    )

    client.post(
        f"/products/{product_id}/restock",
        json={"quantity": 2},
        headers=admin_headers
    )

    client.post(
        f"/products/{product_id}/restock",
        json={"quantity": 3},
        headers=admin_headers
    )

    response = client.get(
        (
            "/admin/inventory/movements"
            f"?product_id={product_id}&skip=1&limit=1"
        ),
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

def test_archived_product_disappears_from_catalog(admin_headers):
    headers = create_test_user(
        "archiveuser1",
        "archiveuser1@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Archived Catalog Product",
            "price": 2000,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    assert product_response.status_code == 201
    product_id = product_response.json()["id"]

    delete_response = client.delete(
        f"/products/{product_id}",
        headers=admin_headers
    )

    assert delete_response.status_code == 204

    response = client.get(
        "/products?search=Archived%20Catalog%20Product"
    )

    assert response.status_code == 200
    assert response.json() == []


def test_archived_product_returns_404(admin_headers):
    headers = create_test_user(
        "archiveuser2",
        "archiveuser2@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Archived Get Product",
            "price": 2100,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    client.delete(
        f"/products/{product_id}",
        headers=admin_headers
    )

    response = client.get(
        f"/products/{product_id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_archived_product_cannot_be_added_to_cart(admin_headers):
    headers = create_test_user(
        "archiveuser3",
        "archiveuser3@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Archived Cart Product",
            "price": 2200,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    client.delete(
        f"/products/{product_id}",
        headers=admin_headers
    )

    response = client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 1
        },
        headers=headers
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_archived_product_cannot_be_deleted_twice(admin_headers):
    headers = create_test_user(
        "archiveuser4",
        "archiveuser4@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Archived Twice Product",
            "price": 2300,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    first_delete = client.delete(
        f"/products/{product_id}",
        headers=admin_headers
    )

    second_delete = client.delete(
        f"/products/{product_id}",
        headers=admin_headers
    )

    assert first_delete.status_code == 204
    assert second_delete.status_code == 404

def test_order_cannot_be_created_with_archived_product(admin_headers):
    headers = create_test_user(
        "archiveuser5",
        "archiveuser5@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Archived Order Product",
            "price": 2400,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    cart_response = client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 1
        },
        headers=headers
    )

    assert cart_response.status_code == 201

    archive_response = client.delete(
        f"/products/{product_id}",
        headers=admin_headers
    )

    assert archive_response.status_code == 204

    order_response = client.post(
        "/orders",
        json={
            "shipping_city": "Kyiv",
            "shipping_street": "Test Street 1",
            "shipping_postal_code": "01001"
        },
        headers=headers
    )

    assert order_response.status_code == 400
    assert (
        order_response.json()["detail"]
        == "Product is no longer available"
    )

def test_expired_promo_code_cannot_be_used(admin_headers):
    headers = create_test_user(
        "promorestrictionuser1",
        "promorestrictionuser1@example.com"
    )

    promo_response = client.post(
        "/promo-codes",
        json={
            "code": "EXPIREDPROMO15",
            "discount_percent": 15,
            "active": True,
            "expires_at": "2020-01-01T00:00:00Z"
        },
        headers=admin_headers
    )

    assert promo_response.status_code == 201

    product_response = client.post(
        "/products",
        json={
            "name": "Expired Promo Product",
            "price": 2000,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    cart_response = client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 1
        },
        headers=headers
    )

    assert cart_response.status_code == 201

    response = client.post(
        "/orders",
        json={
            **SHIPPING_DATA,
            "promo_code": "EXPIREDPROMO15"
        },
        headers=headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Promo code expired"


def test_promo_code_requires_minimum_order_amount(admin_headers):
    headers = create_test_user(
        "promorestrictionuser2",
        "promorestrictionuser2@example.com"
    )

    promo_response = client.post(
        "/promo-codes",
        json={
            "code": "MINIMUMPROMO20",
            "discount_percent": 20,
            "active": True,
            "min_order_amount": 5000
        },
        headers=admin_headers
    )

    assert promo_response.status_code == 201

    product_response = client.post(
        "/products",
        json={
            "name": "Minimum Promo Product",
            "price": 2000,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    cart_response = client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 1
        },
        headers=headers
    )

    assert cart_response.status_code == 201

    response = client.post(
        "/orders",
        json={
            **SHIPPING_DATA,
            "promo_code": "MINIMUMPROMO20"
        },
        headers=headers
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Minimum order amount not reached"
    )


def test_promo_code_usage_limit(admin_headers):
    first_headers = create_test_user(
        "promorestrictionuser3",
        "promorestrictionuser3@example.com"
    )

    second_headers = create_test_user(
        "promorestrictionuser4",
        "promorestrictionuser4@example.com"
    )

    promo_response = client.post(
        "/promo-codes",
        json={
            "code": "LIMITPROMO25",
            "discount_percent": 25,
            "active": True,
            "max_uses": 1
        },
        headers=admin_headers
    )

    assert promo_response.status_code == 201

    first_product = client.post(
        "/products",
        json={
            "name": "Promo Limit Product One",
            "price": 4000,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=first_headers
    )

    first_product_id = first_product.json()["id"]

    client.post(
        "/cart",
        json={
            "product_id": first_product_id,
            "quantity": 1
        },
        headers=first_headers
    )

    first_order = client.post(
        "/orders",
        json={
            **SHIPPING_DATA,
            "promo_code": "LIMITPROMO25"
        },
        headers=first_headers
    )

    assert first_order.status_code == 201

    second_product = client.post(
        "/products",
        json={
            "name": "Promo Limit Product Two",
            "price": 4000,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=second_headers
    )

    second_product_id = second_product.json()["id"]

    client.post(
        "/cart",
        json={
            "product_id": second_product_id,
            "quantity": 1
        },
        headers=second_headers
    )

    second_order = client.post(
        "/orders",
        json={
            **SHIPPING_DATA,
            "promo_code": "LIMITPROMO25"
        },
        headers=second_headers
    )

    assert second_order.status_code == 400
    assert (
        second_order.json()["detail"]
        == "Promo code usage limit reached"
    )


def test_promo_code_used_count_increases(admin_headers):
    headers = create_test_user(
        "promorestrictionuser5",
        "promorestrictionuser5@example.com"
    )

    promo_response = client.post(
        "/promo-codes",
        json={
            "code": "COUNTPROMO10",
            "discount_percent": 10,
            "active": True,
            "max_uses": 5
        },
        headers=admin_headers
    )

    assert promo_response.status_code == 201
    assert promo_response.json()["used_count"] == 0

    product_response = client.post(
        "/products",
        json={
            "name": "Promo Counter Product",
            "price": 3000,
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
        json={
            **SHIPPING_DATA,
            "promo_code": "COUNTPROMO10"
        },
        headers=headers
    )

    assert order_response.status_code == 201

    promo_check = client.get(
        "/promo-codes/COUNTPROMO10"
    )

    assert promo_check.status_code == 200
    assert promo_check.json()["used_count"] == 1


def test_promo_code_without_restrictions_still_works(admin_headers):
    headers = create_test_user(
        "promorestrictionuser6",
        "promorestrictionuser6@example.com"
    )

    promo_response = client.post(
        "/promo-codes",
        json={
            "code": "UNLIMITEDPROMO10",
            "discount_percent": 10,
            "active": True
        },
        headers=admin_headers
    )

    assert promo_response.status_code == 201

    product_response = client.post(
        "/products",
        json={
            "name": "Unlimited Promo Product",
            "price": 5000,
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

    response = client.post(
        "/orders",
        json={
            **SHIPPING_DATA,
            "promo_code": "UNLIMITEDPROMO10"
        },
        headers=headers
    )

    assert response.status_code == 201

    order = response.json()

    assert order["subtotal"] == 5000
    assert order["discount_amount"] == 500
    assert order["total_price"] == 4500
    assert order["promo_code"] == "UNLIMITEDPROMO10"

def test_admin_orders_can_be_filtered_by_user_id(admin_headers):
    headers = create_test_user(
        "adminorderfilter1",
        "adminorderfilter1@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Admin Order Filter Product 1",
            "price": 3210,
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

    assert order_response.status_code == 201

    order = order_response.json()
    user_id = order["user_id"]
    order_id = order["id"]

    response = client.get(
        f"/admin/orders?user_id={user_id}",
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert any(item["id"] == order_id for item in data)
    assert all(item["user_id"] == user_id for item in data)


def test_admin_orders_can_be_filtered_by_total_range(admin_headers):
    headers = create_test_user(
        "adminorderfilter2",
        "adminorderfilter2@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Admin Order Filter Product 2",
            "price": 4321,
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

    assert order_response.status_code == 201

    order_id = order_response.json()["id"]

    response = client.get(
        "/admin/orders?min_total=4300&max_total=4350",
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert any(item["id"] == order_id for item in data)

    assert all(
        4300 <= item["total_price"] <= 4350
        for item in data
    )


def test_admin_orders_support_combined_filters(admin_headers):
    headers = create_test_user(
        "adminorderfilter3",
        "adminorderfilter3@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Admin Combined Filter Product",
            "price": 5432,
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

    assert order_response.status_code == 201

    order = order_response.json()
    user_id = order["user_id"]
    order_id = order["id"]

    response = client.get(
        (
            "/admin/orders"
            f"?user_id={user_id}"
            "&status=pending"
            "&min_total=5400"
            "&max_total=5500"
        ),
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert any(item["id"] == order_id for item in data)

    assert all(
        item["user_id"] == user_id
        and item["status"] == "pending"
        and 5400 <= item["total_price"] <= 5500
        for item in data
    )


def test_admin_orders_support_pagination(admin_headers):
    headers = create_test_user(
        "adminorderfilter4",
        "adminorderfilter4@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Admin Pagination Product",
            "price": 6543,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    for _ in range(3):
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

        assert order_response.status_code == 201

    last_order = order_response.json()
    user_id = last_order["user_id"]

    full_response = client.get(
        f"/admin/orders?user_id={user_id}&limit=10",
        headers=admin_headers
    )

    assert full_response.status_code == 200

    full_data = full_response.json()

    paged_response = client.get(
        f"/admin/orders?user_id={user_id}&skip=1&limit=1",
        headers=admin_headers
    )

    assert paged_response.status_code == 200

    paged_data = paged_response.json()

    assert len(full_data) == 3
    assert len(paged_data) == 1
    assert paged_data[0]["id"] == full_data[1]["id"]


def test_admin_orders_reject_invalid_total_range(admin_headers):
    response = client.get(
        "/admin/orders?min_total=5000&max_total=1000",
        headers=admin_headers
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "min_total cannot be greater than max_total"
    )

def test_admin_can_view_active_and_archived_products(admin_headers):
    headers = create_test_user(
        "adminproductuser1",
        "adminproductuser1@example.com"
    )

    active_response = client.post(
        "/products",
        json={
            "name": "Admin Catalog Pair Active",
            "price": 7100,
            "in_stock": True,
            "stock_quantity": 5
        },
        headers=headers
    )

    archived_response = client.post(
        "/products",
        json={
            "name": "Admin Catalog Pair Archived",
            "price": 7200,
            "in_stock": True,
            "stock_quantity": 5
        },
        headers=headers
    )

    active_id = active_response.json()["id"]
    archived_id = archived_response.json()["id"]

    client.delete(
        f"/products/{archived_id}",
        headers=admin_headers
    )

    response = client.get(
        "/admin/products?search=Admin%20Catalog%20Pair",
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()
    ids = [product["id"] for product in data]

    assert active_id in ids
    assert archived_id in ids


def test_admin_products_can_filter_archived_products(admin_headers):
    headers = create_test_user(
        "adminproductuser2",
        "adminproductuser2@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Archived Admin Filter Product",
            "price": 7300,
            "in_stock": True,
            "stock_quantity": 5
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    client.delete(
        f"/products/{product_id}",
        headers=admin_headers
    )

    response = client.get(
        (
            "/admin/products"
            "?active=false"
            "&search=Archived%20Admin%20Filter%20Product"
        ),
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == product_id
    assert data[0]["is_active"] is False


def test_admin_products_can_filter_active_products(admin_headers):
    headers = create_test_user(
        "adminproductuser3",
        "adminproductuser3@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Active Admin Filter Product",
            "price": 7400,
            "in_stock": True,
            "stock_quantity": 5
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    response = client.get(
        (
            "/admin/products"
            "?active=true"
            "&search=Active%20Admin%20Filter%20Product"
        ),
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == product_id
    assert data[0]["is_active"] is True


def test_admin_can_restore_archived_product(admin_headers):
    headers = create_test_user(
        "adminproductuser4",
        "adminproductuser4@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Restorable Product",
            "price": 7500,
            "in_stock": True,
            "stock_quantity": 5
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    archive_response = client.delete(
        f"/products/{product_id}",
        headers=admin_headers
    )

    assert archive_response.status_code == 204

    hidden_response = client.get(
        f"/products/{product_id}"
    )

    assert hidden_response.status_code == 404

    restore_response = client.post(
        f"/products/{product_id}/restore",
        headers=admin_headers
    )

    assert restore_response.status_code == 200
    assert restore_response.json()["is_active"] is True

    public_response = client.get(
        f"/products/{product_id}"
    )

    assert public_response.status_code == 200
    assert public_response.json()["id"] == product_id


def test_regular_user_cannot_restore_product(admin_headers):
    headers = create_test_user(
        "adminproductuser5",
        "adminproductuser5@example.com"
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Protected Restore Product",
            "price": 7600,
            "in_stock": True,
            "stock_quantity": 5
        },
        headers=headers
    )

    product_id = product_response.json()["id"]

    client.delete(
        f"/products/{product_id}",
        headers=admin_headers
    )

    response = client.post(
        f"/products/{product_id}/restore",
        headers=headers
    )

    assert response.status_code == 403

def test_admin_can_view_all_promo_codes(admin_headers):
    active_response = client.post(
        "/promo-codes",
        json={
            "code": "ADMINPROMOLISTACTIVE",
            "discount_percent": 10,
            "active": True
        },
        headers=admin_headers
    )

    inactive_response = client.post(
        "/promo-codes",
        json={
            "code": "ADMINPROMOLISTINACTIVE",
            "discount_percent": 20,
            "active": False
        },
        headers=admin_headers
    )

    assert active_response.status_code == 201
    assert inactive_response.status_code == 201

    active_id = active_response.json()["id"]
    inactive_id = inactive_response.json()["id"]

    response = client.get(
        "/admin/promo-codes?limit=100",
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()
    ids = [promo["id"] for promo in data]

    assert active_id in ids
    assert inactive_id in ids


def test_admin_can_filter_inactive_promo_codes(admin_headers):
    promo_response = client.post(
        "/promo-codes",
        json={
            "code": "ADMINPROMOINACTIVEFILTER",
            "discount_percent": 15,
            "active": False
        },
        headers=admin_headers
    )

    assert promo_response.status_code == 201

    promo_id = promo_response.json()["id"]

    response = client.get(
        "/admin/promo-codes?active=false&limit=100",
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert any(
        promo["id"] == promo_id
        for promo in data
    )

    assert all(
        promo["active"] is False
        for promo in data
    )


def test_admin_can_update_promo_code(admin_headers):
    promo_response = client.post(
        "/promo-codes",
        json={
            "code": "ADMINPROMOUPDATE",
            "discount_percent": 10,
            "active": True
        },
        headers=admin_headers
    )

    assert promo_response.status_code == 201

    promo_id = promo_response.json()["id"]

    response = client.patch(
        f"/admin/promo-codes/{promo_id}",
        json={
            "discount_percent": 35,
            "active": False,
            "expires_at": "2030-12-31T23:59:59Z",
            "min_order_amount": 2500,
            "max_uses": 50
        },
        headers=admin_headers
    )

    assert response.status_code == 200

    promo = response.json()

    assert promo["id"] == promo_id
    assert promo["code"] == "ADMINPROMOUPDATE"
    assert promo["discount_percent"] == 35
    assert promo["active"] is False
    assert promo["min_order_amount"] == 2500
    assert promo["max_uses"] == 50
    assert promo["expires_at"] is not None


def test_admin_promo_update_returns_404_for_missing_code(
    admin_headers
):
    response = client.patch(
        "/admin/promo-codes/999999999",
        json={
            "discount_percent": 25
        },
        headers=admin_headers
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Promo code not found"


def test_regular_user_cannot_manage_admin_promo_codes(
    admin_headers
):
    headers = create_test_user(
        "adminpromoregularuser",
        "adminpromoregularuser@example.com"
    )

    promo_response = client.post(
        "/promo-codes",
        json={
            "code": "ADMINPROMOPROTECTED",
            "discount_percent": 10,
            "active": True
        },
        headers=admin_headers
    )

    assert promo_response.status_code == 201

    promo_id = promo_response.json()["id"]

    list_response = client.get(
        "/admin/promo-codes",
        headers=headers
    )

    update_response = client.patch(
        f"/admin/promo-codes/{promo_id}",
        json={
            "discount_percent": 50
        },
        headers=headers
    )

    assert list_response.status_code == 403
    assert update_response.status_code == 403

def test_login_returns_refresh_token():
    register_response = client.post(
        "/register",
        json={
            "username": "refreshuser1",
            "email": "refreshuser1@example.com",
            "password": "password123"
        }
    )

    assert register_response.status_code == 201

    response = client.post(
        "/login",
        data={
            "username": "refreshuser1",
            "password": "password123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_refresh_token_returns_new_tokens():
    client.post(
        "/register",
        json={
            "username": "refreshuser2",
            "email": "refreshuser2@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/login",
        data={
            "username": "refreshuser2",
            "password": "password123"
        }
    )

    assert login_response.status_code == 200

    refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        "/refresh",
        json={
            "refresh_token": refresh_token
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    me_response = client.get(
        "/me",
        headers={
            "Authorization": f"Bearer {data['access_token']}"
        }
    )

    assert me_response.status_code == 200
    assert me_response.json()["username"] == "refreshuser2"


def test_access_token_cannot_be_used_as_refresh_token():
    client.post(
        "/register",
        json={
            "username": "refreshuser3",
            "email": "refreshuser3@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/login",
        data={
            "username": "refreshuser3",
            "password": "password123"
        }
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    response = client.post(
        "/refresh",
        json={
            "refresh_token": access_token
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid refresh token"


def test_invalid_refresh_token_is_rejected():
    response = client.post(
        "/refresh",
        json={
            "refresh_token": "this-is-not-a-valid-jwt"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid refresh token"

def test_refresh_token_rotation_revokes_old_token():
    client.post(
        "/register",
        json={
            "username": "rotationuser1",
            "email": "rotationuser1@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/login",
        data={
            "username": "rotationuser1",
            "password": "password123"
        }
    )

    assert login_response.status_code == 200

    old_refresh_token = login_response.json()["refresh_token"]

    refresh_response = client.post(
        "/refresh",
        json={
            "refresh_token": old_refresh_token
        }
    )

    assert refresh_response.status_code == 200

    new_refresh_token = refresh_response.json()["refresh_token"]

    assert new_refresh_token != old_refresh_token

    old_token_response = client.post(
        "/refresh",
        json={
            "refresh_token": old_refresh_token
        }
    )

    assert old_token_response.status_code == 401
    assert (
        old_token_response.json()["detail"]
        == "Invalid refresh token"
    )


def test_rotated_refresh_token_can_be_used():
    client.post(
        "/register",
        json={
            "username": "rotationuser2",
            "email": "rotationuser2@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/login",
        data={
            "username": "rotationuser2",
            "password": "password123"
        }
    )

    first_refresh_token = (
        login_response.json()["refresh_token"]
    )

    first_refresh_response = client.post(
        "/refresh",
        json={
            "refresh_token": first_refresh_token
        }
    )

    assert first_refresh_response.status_code == 200

    second_refresh_token = (
        first_refresh_response.json()["refresh_token"]
    )

    second_refresh_response = client.post(
        "/refresh",
        json={
            "refresh_token": second_refresh_token
        }
    )

    assert second_refresh_response.status_code == 200

    data = second_refresh_response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_logout_revokes_refresh_token():
    client.post(
        "/register",
        json={
            "username": "logoutuser1",
            "email": "logoutuser1@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/login",
        data={
            "username": "logoutuser1",
            "password": "password123"
        }
    )

    assert login_response.status_code == 200

    refresh_token = login_response.json()["refresh_token"]

    logout_response = client.post(
        "/logout",
        json={
            "refresh_token": refresh_token
        }
    )

    assert logout_response.status_code == 204

    refresh_response = client.post(
        "/refresh",
        json={
            "refresh_token": refresh_token
        }
    )

    assert refresh_response.status_code == 401
    assert (
        refresh_response.json()["detail"]
        == "Invalid refresh token"
    )


def test_access_token_cannot_be_used_for_logout():
    client.post(
        "/register",
        json={
            "username": "logoutuser2",
            "email": "logoutuser2@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/login",
        data={
            "username": "logoutuser2",
            "password": "password123"
        }
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    response = client.post(
        "/logout",
        json={
            "refresh_token": access_token
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid refresh token"

def test_logout_all_revokes_all_user_refresh_tokens():
    client.post(
        "/register",
        json={
            "username": "logoutalluser1",
            "email": "logoutalluser1@example.com",
            "password": "password123"
        }
    )

    first_login = client.post(
        "/login",
        data={
            "username": "logoutalluser1",
            "password": "password123"
        }
    )

    second_login = client.post(
        "/login",
        data={
            "username": "logoutalluser1",
            "password": "password123"
        }
    )

    assert first_login.status_code == 200
    assert second_login.status_code == 200

    first_refresh_token = (
        first_login.json()["refresh_token"]
    )

    second_refresh_token = (
        second_login.json()["refresh_token"]
    )

    access_token = first_login.json()["access_token"]

    logout_response = client.post(
        "/logout-all",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert logout_response.status_code == 204

    first_refresh_response = client.post(
        "/refresh",
        json={
            "refresh_token": first_refresh_token
        }
    )

    second_refresh_response = client.post(
        "/refresh",
        json={
            "refresh_token": second_refresh_token
        }
    )

    assert first_refresh_response.status_code == 401
    assert second_refresh_response.status_code == 401

    assert (
        first_refresh_response.json()["detail"]
        == "Invalid refresh token"
    )

    assert (
        second_refresh_response.json()["detail"]
        == "Invalid refresh token"
    )


def test_logout_all_does_not_revoke_other_user_tokens():
    client.post(
        "/register",
        json={
            "username": "logoutalluser2",
            "email": "logoutalluser2@example.com",
            "password": "password123"
        }
    )

    client.post(
        "/register",
        json={
            "username": "logoutalluser3",
            "email": "logoutalluser3@example.com",
            "password": "password123"
        }
    )

    first_login = client.post(
        "/login",
        data={
            "username": "logoutalluser2",
            "password": "password123"
        }
    )

    second_login = client.post(
        "/login",
        data={
            "username": "logoutalluser3",
            "password": "password123"
        }
    )

    first_access_token = (
        first_login.json()["access_token"]
    )

    first_refresh_token = (
        first_login.json()["refresh_token"]
    )

    second_refresh_token = (
        second_login.json()["refresh_token"]
    )

    logout_response = client.post(
        "/logout-all",
        headers={
            "Authorization": f"Bearer {first_access_token}"
        }
    )

    assert logout_response.status_code == 204

    first_refresh_response = client.post(
        "/refresh",
        json={
            "refresh_token": first_refresh_token
        }
    )

    second_refresh_response = client.post(
        "/refresh",
        json={
            "refresh_token": second_refresh_token
        }
    )

    assert first_refresh_response.status_code == 401
    assert second_refresh_response.status_code == 200


def test_logout_all_requires_authentication():
    response = client.post(
        "/logout-all"
    )

    assert response.status_code == 401

def test_user_can_view_active_refresh_sessions():
    client.post(
        "/register",
        json={
            "username": "sessionuser1",
            "email": "sessionuser1@example.com",
            "password": "password123"
        }
    )

    first_login = client.post(
        "/login",
        data={
            "username": "sessionuser1",
            "password": "password123"
        }
    )

    second_login = client.post(
        "/login",
        data={
            "username": "sessionuser1",
            "password": "password123"
        }
    )

    assert first_login.status_code == 200
    assert second_login.status_code == 200

    access_token = first_login.json()["access_token"]

    response = client.get(
        "/sessions",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) >= 2
    assert all(session["revoked"] is False for session in data)


def test_user_can_revoke_single_refresh_session():
    client.post(
        "/register",
        json={
            "username": "sessionuser2",
            "email": "sessionuser2@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/login",
        data={
            "username": "sessionuser2",
            "password": "password123"
        }
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]
    refresh_token = login_response.json()["refresh_token"]

    sessions_response = client.get(
        "/sessions",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert sessions_response.status_code == 200

    sessions = sessions_response.json()

    assert len(sessions) >= 1

    session_id = sessions[0]["id"]

    delete_response = client.delete(
        f"/sessions/{session_id}",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert delete_response.status_code == 204

    refresh_response = client.post(
        "/refresh",
        json={
            "refresh_token": refresh_token
        }
    )

    assert refresh_response.status_code == 401
    assert (
        refresh_response.json()["detail"]
        == "Invalid refresh token"
    )


def test_user_cannot_revoke_another_users_session():
    client.post(
        "/register",
        json={
            "username": "sessionuser3",
            "email": "sessionuser3@example.com",
            "password": "password123"
        }
    )

    client.post(
        "/register",
        json={
            "username": "sessionuser4",
            "email": "sessionuser4@example.com",
            "password": "password123"
        }
    )

    first_login = client.post(
        "/login",
        data={
            "username": "sessionuser3",
            "password": "password123"
        }
    )

    second_login = client.post(
        "/login",
        data={
            "username": "sessionuser4",
            "password": "password123"
        }
    )

    first_access_token = first_login.json()["access_token"]
    second_access_token = second_login.json()["access_token"]

    second_sessions_response = client.get(
        "/sessions",
        headers={
            "Authorization": f"Bearer {second_access_token}"
        }
    )

    assert second_sessions_response.status_code == 200

    second_session_id = (
        second_sessions_response.json()[0]["id"]
    )

    response = client.delete(
        f"/sessions/{second_session_id}",
        headers={
            "Authorization": f"Bearer {first_access_token}"
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


def test_revoked_session_disappears_from_active_sessions():
    client.post(
        "/register",
        json={
            "username": "sessionuser5",
            "email": "sessionuser5@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/login",
        data={
            "username": "sessionuser5",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    sessions_response = client.get(
        "/sessions",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert sessions_response.status_code == 200

    session_id = sessions_response.json()[0]["id"]

    delete_response = client.delete(
        f"/sessions/{session_id}",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert delete_response.status_code == 204

    final_sessions_response = client.get(
        "/sessions",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert final_sessions_response.status_code == 200

    session_ids = [
        session["id"]
        for session in final_sessions_response.json()
    ]

    assert session_id not in session_ids

def test_user_can_change_password():
    client.post(
        "/register",
        json={
            "username": "passwordchangeuser1",
            "email": "passwordchangeuser1@example.com",
            "password": "oldpassword123"
        }
    )

    login_response = client.post(
        "/login",
        data={
            "username": "passwordchangeuser1",
            "password": "oldpassword123"
        }
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    response = client.patch(
        "/me/password",
        json={
            "current_password": "oldpassword123",
            "new_password": "newpassword123"
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 204

    old_login = client.post(
        "/login",
        data={
            "username": "passwordchangeuser1",
            "password": "oldpassword123"
        }
    )

    assert old_login.status_code == 401

    new_login = client.post(
        "/login",
        data={
            "username": "passwordchangeuser1",
            "password": "newpassword123"
        }
    )

    assert new_login.status_code == 200


def test_change_password_rejects_incorrect_current_password():
    client.post(
        "/register",
        json={
            "username": "passwordchangeuser2",
            "email": "passwordchangeuser2@example.com",
            "password": "oldpassword123"
        }
    )

    login_response = client.post(
        "/login",
        data={
            "username": "passwordchangeuser2",
            "password": "oldpassword123"
        }
    )

    access_token = login_response.json()["access_token"]

    response = client.patch(
        "/me/password",
        json={
            "current_password": "wrongpassword123",
            "new_password": "newpassword123"
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Current password is incorrect"
    )


def test_change_password_rejects_same_password():
    client.post(
        "/register",
        json={
            "username": "passwordchangeuser3",
            "email": "passwordchangeuser3@example.com",
            "password": "samepassword123"
        }
    )

    login_response = client.post(
        "/login",
        data={
            "username": "passwordchangeuser3",
            "password": "samepassword123"
        }
    )

    access_token = login_response.json()["access_token"]

    response = client.patch(
        "/me/password",
        json={
            "current_password": "samepassword123",
            "new_password": "samepassword123"
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "New password must be different"
    )


def test_change_password_revokes_refresh_tokens():
    client.post(
        "/register",
        json={
            "username": "passwordchangeuser4",
            "email": "passwordchangeuser4@example.com",
            "password": "oldpassword123"
        }
    )

    login_response = client.post(
        "/login",
        data={
            "username": "passwordchangeuser4",
            "password": "oldpassword123"
        }
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]
    refresh_token = login_response.json()["refresh_token"]

    change_response = client.patch(
        "/me/password",
        json={
            "current_password": "oldpassword123",
            "new_password": "newpassword123"
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert change_response.status_code == 204

    refresh_response = client.post(
        "/refresh",
        json={
            "refresh_token": refresh_token
        }
    )

    assert refresh_response.status_code == 401
    assert (
        refresh_response.json()["detail"]
        == "Invalid refresh token"
    )
def test_admin_can_deactivate_user(admin_headers):
    headers = create_test_user(
        "deactivateuser1",
        "deactivateuser1@example.com"
    )

    me_response = client.get(
        "/me",
        headers=headers
    )

    assert me_response.status_code == 200

    user_id = me_response.json()["id"]

    response = client.patch(
        f"/users/{user_id}/active",
        json={
            "is_active": False
        },
        headers=admin_headers
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_deactivated_user_cannot_login(admin_headers):
    client.post(
        "/register",
        json={
            "username": "deactivateuser2",
            "email": "deactivateuser2@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/login",
        data={
            "username": "deactivateuser2",
            "password": "password123"
        }
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    me_response = client.get(
        "/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    user_id = me_response.json()["id"]

    deactivate_response = client.patch(
        f"/users/{user_id}/active",
        json={
            "is_active": False
        },
        headers=admin_headers
    )

    assert deactivate_response.status_code == 200

    response = client.post(
        "/login",
        data={
            "username": "deactivateuser2",
            "password": "password123"
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Account is disabled"


def test_deactivated_user_access_token_stops_working(admin_headers):
    client.post(
        "/register",
        json={
            "username": "deactivateuser3",
            "email": "deactivateuser3@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/login",
        data={
            "username": "deactivateuser3",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    me_response = client.get(
        "/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    user_id = me_response.json()["id"]

    client.patch(
        f"/users/{user_id}/active",
        json={
            "is_active": False
        },
        headers=admin_headers
    )

    response = client.get(
        "/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 401
    assert (
        response.json()["detail"]
        == "Could not validate credentials"
    )


def test_deactivating_user_revokes_refresh_tokens(admin_headers):
    client.post(
        "/register",
        json={
            "username": "deactivateuser4",
            "email": "deactivateuser4@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/login",
        data={
            "username": "deactivateuser4",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]
    refresh_token = login_response.json()["refresh_token"]

    me_response = client.get(
        "/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    user_id = me_response.json()["id"]

    client.patch(
        f"/users/{user_id}/active",
        json={
            "is_active": False
        },
        headers=admin_headers
    )

    response = client.post(
        "/refresh",
        json={
            "refresh_token": refresh_token
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid refresh token"


def test_admin_can_reactivate_user(admin_headers):
    client.post(
        "/register",
        json={
            "username": "deactivateuser5",
            "email": "deactivateuser5@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/login",
        data={
            "username": "deactivateuser5",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    me_response = client.get(
        "/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    user_id = me_response.json()["id"]

    deactivate_response = client.patch(
        f"/users/{user_id}/active",
        json={
            "is_active": False
        },
        headers=admin_headers
    )

    assert deactivate_response.status_code == 200

    activate_response = client.patch(
        f"/users/{user_id}/active",
        json={
            "is_active": True
        },
        headers=admin_headers
    )

    assert activate_response.status_code == 200
    assert activate_response.json()["is_active"] is True

    new_login = client.post(
        "/login",
        data={
            "username": "deactivateuser5",
            "password": "password123"
        }
    )

    assert new_login.status_code == 200

def test_admin_can_search_users_by_username_and_email(admin_headers):
    headers = create_test_user(
        "usersearchspecial1",
        "usersearchspecial1@example.com"
    )

    me_response = client.get(
        "/me",
        headers=headers
    )

    assert me_response.status_code == 200

    user_id = me_response.json()["id"]

    username_response = client.get(
        "/users?search=usersearchspecial1",
        headers=admin_headers
    )

    assert username_response.status_code == 200
    assert any(
        user["id"] == user_id
        for user in username_response.json()
    )

    email_response = client.get(
        "/users?search=usersearchspecial1%40example.com",
        headers=admin_headers
    )

    assert email_response.status_code == 200
    assert any(
        user["id"] == user_id
        for user in email_response.json()
    )


def test_admin_can_filter_users_by_role(admin_headers):
    user_headers = create_test_user(
        "rolefiltergroup_user",
        "rolefiltergroup_user@example.com"
    )

    admin_user_headers = create_test_user(
        "rolefiltergroup_admin",
        "rolefiltergroup_admin@example.com"
    )

    admin_user_me = client.get(
        "/me",
        headers=admin_user_headers
    )

    admin_user_id = admin_user_me.json()["id"]

    role_response = client.patch(
        f"/users/{admin_user_id}/role",
        json={
            "role": "admin"
        },
        headers=admin_headers
    )

    assert role_response.status_code == 200

    response = client.get(
        "/users?search=rolefiltergroup&role=admin",
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == admin_user_id
    assert data[0]["role"] == "admin"


def test_admin_can_filter_users_by_active_status(admin_headers):
    active_headers = create_test_user(
        "activefiltergroup_active",
        "activefiltergroup_active@example.com"
    )

    inactive_headers = create_test_user(
        "activefiltergroup_inactive",
        "activefiltergroup_inactive@example.com"
    )

    inactive_me = client.get(
        "/me",
        headers=inactive_headers
    )

    inactive_user_id = inactive_me.json()["id"]

    deactivate_response = client.patch(
        f"/users/{inactive_user_id}/active",
        json={
            "is_active": False
        },
        headers=admin_headers
    )

    assert deactivate_response.status_code == 200

    response = client.get(
        "/users?search=activefiltergroup&active=false",
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == inactive_user_id
    assert data[0]["is_active"] is False


def test_admin_users_support_combined_filters(admin_headers):
    headers = create_test_user(
        "combineduserfilter_target",
        "combineduserfilter_target@example.com"
    )

    other_headers = create_test_user(
        "combineduserfilter_other",
        "combineduserfilter_other@example.com"
    )

    me_response = client.get(
        "/me",
        headers=headers
    )

    user_id = me_response.json()["id"]

    response = client.get(
        (
            "/users"
            "?search=combineduserfilter"
            "&role=user"
            "&active=true"
        ),
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert any(
        user["id"] == user_id
        for user in data
    )

    assert all(
        user["role"] == "user"
        and user["is_active"] is True
        for user in data
    )


def test_admin_users_support_pagination(admin_headers):
    first_headers = create_test_user(
        "userpaginationgroup1",
        "userpaginationgroup1@example.com"
    )

    second_headers = create_test_user(
        "userpaginationgroup2",
        "userpaginationgroup2@example.com"
    )

    third_headers = create_test_user(
        "userpaginationgroup3",
        "userpaginationgroup3@example.com"
    )

    full_response = client.get(
        "/users?search=userpaginationgroup&limit=10",
        headers=admin_headers
    )

    assert full_response.status_code == 200

    full_data = full_response.json()

    assert len(full_data) == 3

    paged_response = client.get(
        "/users?search=userpaginationgroup&skip=1&limit=1",
        headers=admin_headers
    )

    assert paged_response.status_code == 200

    paged_data = paged_response.json()

    assert len(paged_data) == 1
    assert paged_data[0]["id"] == full_data[1]["id"]

def test_user_role_change_creates_audit_log(admin_headers):
    headers = create_test_user(
        "auditroleuser1",
        "auditroleuser1@example.com"
    )

    me_response = client.get(
        "/me",
        headers=headers
    )

    assert me_response.status_code == 200

    user_id = me_response.json()["id"]

    role_response = client.patch(
        f"/users/{user_id}/role",
        json={
            "role": "admin"
        },
        headers=admin_headers
    )

    assert role_response.status_code == 200
    assert role_response.json()["role"] == "admin"

    audit_response = client.get(
        (
            "/admin/audit-logs"
            "?action=user_role_changed"
            "&entity_type=user"
            f"&entity_id={user_id}"
        ),
        headers=admin_headers
    )

    assert audit_response.status_code == 200

    data = audit_response.json()

    assert len(data) == 1

    audit_log = data[0]

    assert audit_log["action"] == "user_role_changed"
    assert audit_log["entity_type"] == "user"
    assert audit_log["entity_id"] == user_id
    assert audit_log["actor_user_id"] is not None
    assert audit_log["details"] == "role: user -> admin"

def test_user_deactivation_creates_audit_log(admin_headers):
    headers = create_test_user(
        "auditdeactivateuser1",
        "auditdeactivateuser1@example.com"
    )

    me_response = client.get(
        "/me",
        headers=headers
    )

    assert me_response.status_code == 200

    user_id = me_response.json()["id"]

    deactivate_response = client.patch(
        f"/users/{user_id}/active",
        json={
            "is_active": False
        },
        headers=admin_headers
    )

    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["is_active"] is False

    audit_response = client.get(
        "/admin/audit-logs",
        params={
            "action": "user_deactivated",
            "entity_type": "user",
            "entity_id": user_id
        },
        headers=admin_headers
    )

    assert audit_response.status_code == 200

    data = audit_response.json()

    assert len(data) == 1

    audit_log = data[0]

    assert audit_log["action"] == "user_deactivated"
    assert audit_log["entity_type"] == "user"
    assert audit_log["entity_id"] == user_id
    assert audit_log["actor_user_id"] is not None
    assert audit_log["details"] == (
        "is_active: True -> False"
    )


def test_user_activation_creates_audit_log(admin_headers):
    headers = create_test_user(
        "auditactivateuser1",
        "auditactivateuser1@example.com"
    )

    me_response = client.get(
        "/me",
        headers=headers
    )

    assert me_response.status_code == 200

    user_id = me_response.json()["id"]

    deactivate_response = client.patch(
        f"/users/{user_id}/active",
        json={
            "is_active": False
        },
        headers=admin_headers
    )

    assert deactivate_response.status_code == 200

    activate_response = client.patch(
        f"/users/{user_id}/active",
        json={
            "is_active": True
        },
        headers=admin_headers
    )

    assert activate_response.status_code == 200
    assert activate_response.json()["is_active"] is True

    audit_response = client.get(
        "/admin/audit-logs",
        params={
            "action": "user_activated",
            "entity_type": "user",
            "entity_id": user_id
        },
        headers=admin_headers
    )

    assert audit_response.status_code == 200

    data = audit_response.json()

    assert len(data) == 1

    audit_log = data[0]

    assert audit_log["action"] == "user_activated"
    assert audit_log["entity_type"] == "user"
    assert audit_log["entity_id"] == user_id
    assert audit_log["actor_user_id"] is not None
    assert audit_log["details"] == (
        "is_active: False -> True"
    )

def test_product_archiving_creates_audit_log(admin_headers):
    product_response = client.post(
        "/products",
        json={
            "name": "Audit Archive Product",
            "price": 1500,
            "in_stock": True,
            "stock_quantity": 3
        },
        headers=admin_headers
    )

    assert product_response.status_code == 201

    product = product_response.json()
    product_id = product["id"]

    archive_response = client.delete(
        f"/products/{product_id}",
        headers=admin_headers
    )

    assert archive_response.status_code == 204

    audit_response = client.get(
        "/admin/audit-logs",
        params={
            "action": "product_archived",
            "entity_type": "product",
            "entity_id": product_id
        },
        headers=admin_headers
    )

    assert audit_response.status_code == 200

    data = audit_response.json()

    assert len(data) == 1

    audit_log = data[0]

    assert audit_log["action"] == "product_archived"
    assert audit_log["entity_type"] == "product"
    assert audit_log["entity_id"] == product_id
    assert audit_log["actor_user_id"] is not None
    assert audit_log["details"] == (
        "product_name: Audit Archive Product"
    )


def test_product_restoring_creates_audit_log(admin_headers):
    product_response = client.post(
        "/products",
        json={
            "name": "Audit Restore Product",
            "price": 1700,
            "in_stock": True,
            "stock_quantity": 4
        },
        headers=admin_headers
    )

    assert product_response.status_code == 201

    product = product_response.json()
    product_id = product["id"]

    archive_response = client.delete(
        f"/products/{product_id}",
        headers=admin_headers
    )

    assert archive_response.status_code == 204

    restore_response = client.post(
        f"/products/{product_id}/restore",
        headers=admin_headers
    )

    assert restore_response.status_code == 200
    assert restore_response.json()["is_active"] is True

    audit_response = client.get(
        "/admin/audit-logs",
        params={
            "action": "product_restored",
            "entity_type": "product",
            "entity_id": product_id
        },
        headers=admin_headers
    )

    assert audit_response.status_code == 200

    data = audit_response.json()

    assert len(data) == 1

    audit_log = data[0]

    assert audit_log["action"] == "product_restored"
    assert audit_log["entity_type"] == "product"
    assert audit_log["entity_id"] == product_id
    assert audit_log["actor_user_id"] is not None
    assert audit_log["details"] == (
        "product_name: Audit Restore Product"
    )

def test_restock_creates_audit_log(admin_headers):
    product_response = client.post(
        "/products",
        json={
            "name": "Audit Restock Product",
            "price": 2100,
            "in_stock": True,
            "stock_quantity": 2
        },
        headers=admin_headers
    )

    assert product_response.status_code == 201

    product_id = product_response.json()["id"]

    restock_response = client.post(
        f"/products/{product_id}/restock",
        json={
            "quantity": 5
        },
        headers=admin_headers
    )

    assert restock_response.status_code == 200
    assert restock_response.json()["stock_quantity"] == 7

    audit_response = client.get(
        "/admin/audit-logs",
        params={
            "action": "stock_restocked",
            "entity_type": "product",
            "entity_id": product_id
        },
        headers=admin_headers
    )

    assert audit_response.status_code == 200

    data = audit_response.json()

    assert len(data) == 1

    audit_log = data[0]

    assert audit_log["action"] == "stock_restocked"
    assert audit_log["entity_type"] == "product"
    assert audit_log["entity_id"] == product_id
    assert audit_log["actor_user_id"] is not None
    assert audit_log["details"] == "quantity_added: 5"


def test_stock_adjustment_creates_audit_log(admin_headers):
    product_response = client.post(
        "/products",
        json={
            "name": "Audit Adjust Product",
            "price": 2600,
            "in_stock": True,
            "stock_quantity": 10
        },
        headers=admin_headers
    )

    assert product_response.status_code == 201

    product_id = product_response.json()["id"]

    adjust_response = client.post(
        f"/products/{product_id}/adjust-stock",
        json={
            "quantity_change": -3,
            "reason": "damaged items"
        },
        headers=admin_headers
    )

    assert adjust_response.status_code == 200
    assert adjust_response.json()["stock_quantity"] == 7

    audit_response = client.get(
        "/admin/audit-logs",
        params={
            "action": "stock_adjusted",
            "entity_type": "product",
            "entity_id": product_id
        },
        headers=admin_headers
    )

    assert audit_response.status_code == 200

    data = audit_response.json()

    assert len(data) == 1

    audit_log = data[0]

    assert audit_log["action"] == "stock_adjusted"
    assert audit_log["entity_type"] == "product"
    assert audit_log["entity_id"] == product_id
    assert audit_log["actor_user_id"] is not None
    assert audit_log["details"] == (
        "quantity_change: -3; "
        "reason: damaged items"
    )

def test_promo_code_update_creates_audit_log(admin_headers):
    import uuid

    promo_code_value = (
        f"AUDIT{uuid.uuid4().hex[:10].upper()}"
    )

    create_response = client.post(
        "/promo-codes",
        json={
            "code": promo_code_value,
            "discount_percent": 10,
            "active": True,
            "min_order_amount": 0
        },
        headers=admin_headers
    )

    assert create_response.status_code == 201

    promo_code = create_response.json()
    promo_code_id = promo_code["id"]

    update_response = client.patch(
        f"/admin/promo-codes/{promo_code_id}",
        json={
            "discount_percent": 25,
            "active": False
        },
        headers=admin_headers
    )

    assert update_response.status_code == 200

    updated_promo = update_response.json()

    assert updated_promo["discount_percent"] == 25
    assert updated_promo["active"] is False

    audit_response = client.get(
        "/admin/audit-logs",
        params={
            "action": "promo_code_updated",
            "entity_type": "promo_code",
            "entity_id": promo_code_id
        },
        headers=admin_headers
    )

    assert audit_response.status_code == 200

    data = audit_response.json()

    assert len(data) == 1

    audit_log = data[0]

    assert audit_log["action"] == "promo_code_updated"
    assert audit_log["entity_type"] == "promo_code"
    assert audit_log["entity_id"] == promo_code_id
    assert audit_log["actor_user_id"] is not None
    assert audit_log["details"] == (
        "updated_fields: discount_percent, active"
    )

def test_regular_user_cannot_view_audit_logs():
    import uuid

    suffix = uuid.uuid4().hex[:8]

    headers = create_test_user(
        f"auditviewer_{suffix}",
        f"auditviewer_{suffix}@example.com"
    )

    response = client.get(
        "/admin/audit-logs",
        headers=headers
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_admin_can_filter_audit_logs_by_entity(admin_headers):
    import uuid

    suffix = uuid.uuid4().hex[:8]

    headers = create_test_user(
        f"auditentity_{suffix}",
        f"auditentity_{suffix}@example.com"
    )

    me_response = client.get(
        "/me",
        headers=headers
    )

    assert me_response.status_code == 200

    user_id = me_response.json()["id"]

    role_response = client.patch(
        f"/users/{user_id}/role",
        json={
            "role": "admin"
        },
        headers=admin_headers
    )

    assert role_response.status_code == 200

    response = client.get(
        "/admin/audit-logs",
        params={
            "action": "user_role_changed",
            "entity_type": "user",
            "entity_id": user_id
        },
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["action"] == "user_role_changed"
    assert data[0]["entity_type"] == "user"
    assert data[0]["entity_id"] == user_id


def test_admin_can_filter_audit_logs_by_actor(admin_headers):
    import uuid

    suffix = uuid.uuid4().hex[:8]

    actor_headers = create_test_user(
        f"auditactor_{suffix}",
        f"auditactor_{suffix}@example.com"
    )

    actor_me_response = client.get(
        "/me",
        headers=actor_headers
    )

    assert actor_me_response.status_code == 200

    actor_id = actor_me_response.json()["id"]

    promote_actor_response = client.patch(
        f"/users/{actor_id}/role",
        json={
            "role": "admin"
        },
        headers=admin_headers
    )

    assert promote_actor_response.status_code == 200

    target_headers = create_test_user(
        f"audittarget_{suffix}",
        f"audittarget_{suffix}@example.com"
    )

    target_me_response = client.get(
        "/me",
        headers=target_headers
    )

    assert target_me_response.status_code == 200

    target_id = target_me_response.json()["id"]

    role_response = client.patch(
        f"/users/{target_id}/role",
        json={
            "role": "admin"
        },
        headers=actor_headers
    )

    assert role_response.status_code == 200

    response = client.get(
        "/admin/audit-logs",
        params={
            "actor_user_id": actor_id,
            "action": "user_role_changed"
        },
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["actor_user_id"] == actor_id
    assert data[0]["entity_id"] == target_id


def test_admin_audit_logs_support_pagination(admin_headers):
    import uuid

    suffix = uuid.uuid4().hex[:8]

    actor_headers = create_test_user(
        f"auditpageactor_{suffix}",
        f"auditpageactor_{suffix}@example.com"
    )

    actor_me_response = client.get(
        "/me",
        headers=actor_headers
    )

    assert actor_me_response.status_code == 200

    actor_id = actor_me_response.json()["id"]

    promote_response = client.patch(
        f"/users/{actor_id}/role",
        json={
            "role": "admin"
        },
        headers=admin_headers
    )

    assert promote_response.status_code == 200

    target_ids = []

    for index in range(3):
        target_headers = create_test_user(
            f"auditpagetarget{index}_{suffix}",
            f"auditpagetarget{index}_{suffix}@example.com"
        )

        target_me_response = client.get(
            "/me",
            headers=target_headers
        )

        assert target_me_response.status_code == 200

        target_id = target_me_response.json()["id"]
        target_ids.append(target_id)

        role_response = client.patch(
            f"/users/{target_id}/role",
            json={
                "role": "admin"
            },
            headers=actor_headers
        )

        assert role_response.status_code == 200

    full_response = client.get(
        "/admin/audit-logs",
        params={
            "actor_user_id": actor_id,
            "action": "user_role_changed",
            "limit": 10
        },
        headers=admin_headers
    )

    assert full_response.status_code == 200

    full_data = full_response.json()

    assert len(full_data) == 3

    page_response = client.get(
        "/admin/audit-logs",
        params={
            "actor_user_id": actor_id,
            "action": "user_role_changed",
            "skip": 1,
            "limit": 1
        },
        headers=admin_headers
    )

    assert page_response.status_code == 200

    page_data = page_response.json()

    assert len(page_data) == 1
    assert page_data[0]["id"] == full_data[1]["id"]

def test_refresh_token_cannot_be_used_as_access_token():
    import uuid

    suffix = uuid.uuid4().hex[:10]

    username = f"tokentype_{suffix}"
    email = f"tokentype_{suffix}@example.com"
    password = "password123"

    register_response = client.post(
        "/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/login",
        data={
            "username": username,
            "password": password
        }
    )

    assert login_response.status_code == 200

    tokens = login_response.json()

    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    access_response = client.get(
        "/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert access_response.status_code == 200
    assert access_response.json()["username"] == username

    refresh_as_access_response = client.get(
        "/me",
        headers={
            "Authorization": f"Bearer {refresh_token}"
        }
    )

    assert refresh_as_access_response.status_code == 401

def test_expired_refresh_session_is_not_listed(
    db_session
):
    import uuid
    from datetime import datetime, timedelta, timezone

    from auth import decode_refresh_token
    from models import RefreshToken

    suffix = uuid.uuid4().hex[:10]

    username = f"expiredsession_{suffix}"
    email = f"expiredsession_{suffix}@example.com"
    password = "password123"

    register_response = client.post(
        "/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/login",
        data={
            "username": username,
            "password": password
        }
    )

    assert login_response.status_code == 200

    tokens = login_response.json()

    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    payload = decode_refresh_token(
        refresh_token
    )

    assert payload is not None

    jti = payload["jti"]

    refresh_session = (
        db_session.query(RefreshToken)
        .filter(
            RefreshToken.jti == jti
        )
        .first()
    )

    assert refresh_session is not None

    refresh_session_id = refresh_session.id

    refresh_session.expires_at = (
        datetime.now(timezone.utc)
        - timedelta(minutes=1)
    )

    db_session.commit()

    sessions_response = client.get(
        "/sessions",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert sessions_response.status_code == 200

    sessions = sessions_response.json()

    assert all(
        session["id"] != refresh_session_id
        for session in sessions
    )

def test_user_can_update_own_username():
    import uuid

    suffix = uuid.uuid4().hex[:8]

    username = f"profileuser_{suffix}"
    email = f"profileuser_{suffix}@example.com"
    password = "password123"

    register_response = client.post(
        "/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/login",
        data={
            "username": username,
            "password": password
        }
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    new_username = f"updated_{suffix}"

    update_response = client.patch(
        "/me",
        json={
            "username": new_username
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert update_response.status_code == 200
    assert update_response.json()["username"] == new_username
    assert update_response.json()["email"] == email


def test_user_can_update_own_email():
    import uuid

    suffix = uuid.uuid4().hex[:8]

    username = f"profileemail_{suffix}"
    email = f"profileemail_{suffix}@example.com"
    password = "password123"

    register_response = client.post(
        "/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/login",
        data={
            "username": username,
            "password": password
        }
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    new_email = f"updated_{suffix}@example.com"

    update_response = client.patch(
        "/me",
        json={
            "email": new_email
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert update_response.status_code == 200
    assert update_response.json()["username"] == username
    assert update_response.json()["email"] == new_email


def test_user_cannot_use_existing_username():
    import uuid

    suffix = uuid.uuid4().hex[:8]

    first_username = f"profilefirst_{suffix}"
    second_username = f"profilesecond_{suffix}"

    first_email = f"profilefirst_{suffix}@example.com"
    second_email = f"profilesecond_{suffix}@example.com"

    password = "password123"

    first_register = client.post(
        "/register",
        json={
            "username": first_username,
            "email": first_email,
            "password": password
        }
    )

    assert first_register.status_code == 201

    second_register = client.post(
        "/register",
        json={
            "username": second_username,
            "email": second_email,
            "password": password
        }
    )

    assert second_register.status_code == 201

    second_login = client.post(
        "/login",
        data={
            "username": second_username,
            "password": password
        }
    )

    assert second_login.status_code == 200

    access_token = second_login.json()["access_token"]

    update_response = client.patch(
        "/me",
        json={
            "username": first_username
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert update_response.status_code == 400
    assert update_response.json()["detail"] == (
        "Username already exists"
    )


def test_user_cannot_use_existing_email():
    import uuid

    suffix = uuid.uuid4().hex[:8]

    first_username = f"emailfirst_{suffix}"
    second_username = f"emailsecond_{suffix}"

    first_email = f"emailfirst_{suffix}@example.com"
    second_email = f"emailsecond_{suffix}@example.com"

    password = "password123"

    first_register = client.post(
        "/register",
        json={
            "username": first_username,
            "email": first_email,
            "password": password
        }
    )

    assert first_register.status_code == 201

    second_register = client.post(
        "/register",
        json={
            "username": second_username,
            "email": second_email,
            "password": password
        }
    )

    assert second_register.status_code == 201

    second_login = client.post(
        "/login",
        data={
            "username": second_username,
            "password": password
        }
    )

    assert second_login.status_code == 200

    access_token = second_login.json()["access_token"]

    update_response = client.patch(
        "/me",
        json={
            "email": first_email
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert update_response.status_code == 400
    assert update_response.json()["detail"] == (
        "Email already exists"
    )


def test_empty_profile_update_keeps_user_unchanged():
    import uuid

    suffix = uuid.uuid4().hex[:8]

    username = f"profileempty_{suffix}"
    email = f"profileempty_{suffix}@example.com"
    password = "password123"

    register_response = client.post(
        "/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/login",
        data={
            "username": username,
            "password": password
        }
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    update_response = client.patch(
        "/me",
        json={},
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert update_response.status_code == 200
    assert update_response.json()["username"] == username
    assert update_response.json()["email"] == email

def test_username_change_updates_login_credentials():
    import uuid

    suffix = uuid.uuid4().hex[:8]

    old_username = f"oldlogin_{suffix}"
    new_username = f"newlogin_{suffix}"
    email = f"loginchange_{suffix}@example.com"
    password = "password123"

    register_response = client.post(
        "/register",
        json={
            "username": old_username,
            "email": email,
            "password": password
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/login",
        data={
            "username": old_username,
            "password": password
        }
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    update_response = client.patch(
        "/me",
        json={
            "username": new_username
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert update_response.status_code == 200
    assert update_response.json()["username"] == new_username

    old_login_response = client.post(
        "/login",
        data={
            "username": old_username,
            "password": password
        }
    )

    assert old_login_response.status_code == 401

    new_login_response = client.post(
        "/login",
        data={
            "username": new_username,
            "password": password
        }
    )

    assert new_login_response.status_code == 200
    assert "access_token" in new_login_response.json()

def test_tokens_remain_valid_after_username_change():
    import uuid

    suffix = uuid.uuid4().hex[:8]

    old_username = f"tokenold_{suffix}"
    new_username = f"tokennew_{suffix}"
    email = f"tokenrename_{suffix}@example.com"
    password = "password123"

    register_response = client.post(
        "/register",
        json={
            "username": old_username,
            "email": email,
            "password": password
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/login",
        data={
            "username": old_username,
            "password": password
        }
    )

    assert login_response.status_code == 200

    tokens = login_response.json()

    old_access_token = tokens["access_token"]
    old_refresh_token = tokens["refresh_token"]

    update_response = client.patch(
        "/me",
        json={
            "username": new_username
        },
        headers={
            "Authorization": f"Bearer {old_access_token}"
        }
    )

    assert update_response.status_code == 200
    assert update_response.json()["username"] == new_username

    # Старый access token всё ещё должен работать,
    # потому что sub теперь содержит user_id.
    me_response = client.get(
        "/me",
        headers={
            "Authorization": f"Bearer {old_access_token}"
        }
    )

    assert me_response.status_code == 200
    assert me_response.json()["username"] == new_username

    # Старый refresh token также должен работать
    # после изменения username.
    refresh_response = client.post(
        "/refresh",
        json={
            "refresh_token": old_refresh_token
        }
    )

    assert refresh_response.status_code == 200

    refreshed_tokens = refresh_response.json()

    assert "access_token" in refreshed_tokens
    assert "refresh_token" in refreshed_tokens

    new_access_token = refreshed_tokens["access_token"]

    final_me_response = client.get(
        "/me",
        headers={
            "Authorization": f"Bearer {new_access_token}"
        }
    )

    assert final_me_response.status_code == 200
    assert final_me_response.json()["username"] == new_username

def test_profile_update_creates_audit_log(admin_headers):
    import uuid

    suffix = uuid.uuid4().hex[:8]

    username = f"auditprofile_{suffix}"
    email = f"auditprofile_{suffix}@example.com"
    password = "password123"

    register_response = client.post(
        "/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/login",
        data={
            "username": username,
            "password": password
        }
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    user_headers = {
        "Authorization": f"Bearer {access_token}"
    }

    me_response = client.get(
        "/me",
        headers=user_headers
    )

    assert me_response.status_code == 200

    user_id = me_response.json()["id"]

    new_username = f"auditupdated_{suffix}"
    new_email = f"auditupdated_{suffix}@example.com"

    update_response = client.patch(
        "/me",
        json={
            "username": new_username,
            "email": new_email
        },
        headers=user_headers
    )

    assert update_response.status_code == 200
    assert update_response.json()["username"] == new_username
    assert update_response.json()["email"] == new_email

    audit_response = client.get(
        "/admin/audit-logs",
        params={
            "action": "user_profile_updated",
            "entity_type": "user",
            "entity_id": user_id
        },
        headers=admin_headers
    )

    assert audit_response.status_code == 200

    data = audit_response.json()

    assert len(data) == 1

    audit_log = data[0]

    assert audit_log["action"] == "user_profile_updated"
    assert audit_log["entity_type"] == "user"
    assert audit_log["entity_id"] == user_id
    assert audit_log["actor_user_id"] == user_id
    assert audit_log["details"] == (
        "updated_fields: username, email"
    )

def test_empty_profile_update_does_not_create_audit_log(
    admin_headers
):
    import uuid

    suffix = uuid.uuid4().hex[:8]

    username = f"auditprofileempty_{suffix}"
    email = f"auditprofileempty_{suffix}@example.com"
    password = "password123"

    register_response = client.post(
        "/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/login",
        data={
            "username": username,
            "password": password
        }
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    user_headers = {
        "Authorization": f"Bearer {access_token}"
    }

    me_response = client.get(
        "/me",
        headers=user_headers
    )

    assert me_response.status_code == 200

    user_id = me_response.json()["id"]

    update_response = client.patch(
        "/me",
        json={},
        headers=user_headers
    )

    assert update_response.status_code == 200
    assert update_response.json()["username"] == username
    assert update_response.json()["email"] == email

    audit_response = client.get(
        "/admin/audit-logs",
        params={
            "action": "user_profile_updated",
            "entity_type": "user",
            "entity_id": user_id
        },
        headers=admin_headers
    )

    assert audit_response.status_code == 200
    assert audit_response.json() == []

def test_registration_normalizes_email_to_lowercase():
    import uuid

    suffix = uuid.uuid4().hex[:8]

    username = f"emailnormreg_{suffix}"
    raw_email = f"EmailNormREG_{suffix}@Example.COM"
    expected_email = raw_email.lower()

    register_response = client.post(
        "/register",
        json={
            "username": username,
            "email": raw_email,
            "password": "password123"
        }
    )

    assert register_response.status_code == 201
    assert register_response.json()["email"] == expected_email


def test_profile_update_normalizes_email_to_lowercase():
    import uuid

    suffix = uuid.uuid4().hex[:8]

    username = f"emailnormprofile_{suffix}"
    email = f"emailnormprofile_{suffix}@example.com"
    password = "password123"

    register_response = client.post(
        "/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/login",
        data={
            "username": username,
            "password": password
        }
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    raw_new_email = f"UpdatedEmail_{suffix}@Example.COM"
    expected_email = raw_new_email.lower()

    update_response = client.patch(
        "/me",
        json={
            "email": raw_new_email
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert update_response.status_code == 200
    assert update_response.json()["email"] == expected_email


def test_email_duplicate_check_is_case_insensitive():
    import uuid

    suffix = uuid.uuid4().hex[:8]

    first_username = f"emailcasefirst_{suffix}"
    second_username = f"emailcasesecond_{suffix}"

    first_email = f"CaseEmail_{suffix}@Example.COM"
    second_email = first_email.lower()

    first_register = client.post(
        "/register",
        json={
            "username": first_username,
            "email": first_email,
            "password": "password123"
        }
    )

    assert first_register.status_code == 201

    second_register = client.post(
        "/register",
        json={
            "username": second_username,
            "email": second_email,
            "password": "password123"
        }
    )

    assert second_register.status_code in (400, 409)

def test_registration_trims_username():
    import uuid

    suffix = uuid.uuid4().hex[:8]

    raw_username = f"   trimreg_{suffix}   "
    expected_username = f"trimreg_{suffix}"
    email = f"trimreg_{suffix}@example.com"

    response = client.post(
        "/register",
        json={
            "username": raw_username,
            "email": email,
            "password": "password123"
        }
    )

    assert response.status_code == 201
    assert response.json()["username"] == expected_username


def test_profile_update_trims_username():
    import uuid

    suffix = uuid.uuid4().hex[:8]

    username = f"trimprofile_{suffix}"
    email = f"trimprofile_{suffix}@example.com"
    password = "password123"

    register_response = client.post(
        "/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/login",
        data={
            "username": username,
            "password": password
        }
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    raw_new_username = f"   updatedtrim_{suffix}   "
    expected_username = f"updatedtrim_{suffix}"

    update_response = client.patch(
        "/me",
        json={
            "username": raw_new_username
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert update_response.status_code == 200
    assert update_response.json()["username"] == expected_username


def test_username_with_only_spaces_is_rejected():
    import uuid

    suffix = uuid.uuid4().hex[:8]

    response = client.post(
        "/register",
        json={
            "username": "     ",
            "email": f"spaces_{suffix}@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 422

def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "database": "ok"
    }


def test_openapi_metadata():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    data = response.json()

    assert data["info"]["title"] == "E-Commerce REST API"
    assert data["info"]["version"] == "1.0.2"