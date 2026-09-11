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