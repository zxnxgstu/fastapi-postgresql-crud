# FastAPI PostgreSQL CRUD API

![Tests](https://github.com/zxnxgstu/fastapi-postgresql-crud/actions/workflows/tests.yml/badge.svg)

REST API для управления товарами, созданный на FastAPI с PostgreSQL.

## Technologies

- Python 3.13
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- Alembic
- Docker
- Docker Compose
- Pytest
- GitHub Actions

## Features
- User registration
- User login
- JWT authentication
- Password hashing
- Protected product management endpoints
- Current user endpoint
- Create products
- Get all products
- Get product by ID
- Update products
- Delete products
- Search products by name
- Filter products by stock status
- Pagination
- Input validation
- HTTP error handling
- Database migrations with Alembic
- Docker support
- Automated tests
- CI with GitHub Actions
- User roles: `user` and `admin`
- Role-based access control
- Admin-only user management
- Admin can change user roles
- Product categories
- Products can be assigned to categories
- Product filtering by category
- Admin-only category creation
- Shopping cart
- Add products to cart
- Update cart item quantity
- Remove products from cart
- User-specific cart isolation
- Order creation from shopping cart
- Order history
- Order item price snapshots
- Automatic cart cleanup after checkout
- Admin order management
- Order status management
- Product stock quantity
- Stock validation when adding products to cart
- Automatic stock reduction after order creation
- Automatic out-of-stock status when quantity reaches zero
- Shipping address for orders
- Shipping city, street and postal code stored with each order
- Shipping address validation during checkout
- Product search by name
- Product filtering by category and stock status
- Product sorting by id, name, price and stock quantity
- Pagination with skip and limit
- Query parameter validation
- Order filtering by status
- Pagination for user orders
- Pagination for admin order management
- Order query parameter validation
- Promo codes with percentage discounts
- Admin-only promo code creation
- Active/inactive promo code validation
- Promo code discounts applied during checkout
- Applied promo code and discount stored in orders

## API endpoints

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/register` | Register new user | No |
| POST | `/login` | Login and get JWT token | No |
| GET | `/me` | Get current user | Yes |
| GET | `/users` | Get all users | Admin |
| PATCH | `/users/{user_id}/role` | Change user role | Admin |
| GET | `/products` | Get products | No |
| GET | `/products/{product_id}` | Get product by ID | No |
| POST | `/products` | Create product | Yes |
| PUT | `/products/{product_id}` | Update product | Yes |
| DELETE | `/products/{product_id}` | Delete product | Admin |
| GET | `/categories` | Get all categories | No |
| GET | `/categories/{category_id}` | Get category by ID | No |
| POST | `/categories` | Create category | Admin |
| GET | `/cart` | Get current user's cart | Yes |
| POST | `/cart` | Add product to cart | Yes |
| PATCH | `/cart/{item_id}` | Update cart item quantity | Yes |
| DELETE | `/cart/{item_id}` | Remove item from cart | Yes |
| POST | `/orders` | Create order from cart | Yes |
| GET | `/orders` | Get current user's orders | Yes |
| GET | `/orders/{order_id}` | Get current user's order | Yes |
| GET | `/admin/orders` | Get all orders | Admin |
| PATCH | `/admin/orders/{order_id}/status` | Change order status | Admin |

## Product filtering and pagination

Products can be filtered by name, stock status and category:

```text
GET /products?search=Keyboard&in_stock=true&category_id=1&skip=0&limit=10
```text
GET /products?search=Keyboard&in_stock=true&category_id=1&skip=0&limit=10
```

The project currently includes 53 automated API tests.