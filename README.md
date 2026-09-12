# E-Commerce REST API

![Tests](https://github.com/zxnxgstu/fastapi-postgresql-crud/actions/workflows/tests.yml/badge.svg)

Production-style REST API for an e-commerce platform built with FastAPI, PostgreSQL, SQLAlchemy and JWT authentication.

The project includes authentication, role-based access control, product and inventory management, shopping cart, orders, payments, delivery tracking, promo codes, reviews, analytics, audit logging, Docker support, database migrations and automated CI testing.

## Tech Stack

- Python 3.13
- FastAPI
- PostgreSQL 18
- SQLAlchemy 2
- Pydantic 2
- Alembic
- JWT / PyJWT
- pwdlib / Argon2
- Docker
- Docker Compose
- Pytest
- GitHub Actions
- Uvicorn

## Main Features

### Authentication and Users

- User registration and login
- JWT access and refresh tokens
- Separate access and refresh token types
- Refresh token rotation
- Database-backed refresh sessions
- Logout and logout from all devices
- Individual session revocation
- Password changes
- User account activation and deactivation
- Role-based access control
- `user` and `admin` roles
- User profile updates
- Username and email uniqueness validation
- Email normalization
- Username whitespace normalization
- Stable user ID stored in JWT subject
- Expired refresh sessions automatically excluded

### Products and Categories

- Product CRUD
- Product categories
- Search, filtering, sorting and pagination
- Product stock quantities
- Product archiving and restoring
- Price history
- Wishlist support
- Product reviews and ratings
- Price-drop notifications

### Shopping Cart and Orders

- User-specific shopping carts
- Add, update and remove cart items
- Order creation from cart
- Order history
- Order item price snapshots
- Order subtotal, discounts, delivery price and final total
- Customer notes
- Order cancellation
- Automatic stock reduction and restoration
- Order status workflow
- Complete order status history

### Payments and Refunds

- Payment simulation
- One payment per order
- Payment amount snapshots
- Automatic order status updates
- Refund support
- Automatic stock restoration after refunds
- Duplicate payment and refund protection

### Promo Codes

- Percentage discounts
- Expiration dates
- Minimum order amount
- Usage limits
- Usage counter
- Active/inactive status
- Admin promo code management

### Delivery and Shipment Tracking

- Saved user addresses
- Default delivery address
- Delivery methods
- Delivery pricing
- Delivery snapshot data stored in orders
- Shipping carriers and tracking numbers
- Estimated delivery dates
- Shipment event history
- Strict shipment status sequence
- Shipment tracking history
- Automatic order completion after delivery
- Actual `delivered_at` timestamp

### Inventory Management

- Stock movement history
- Manual restocking
- Manual stock adjustment
- Low-stock monitoring
- Inventory summary
- Global stock movement journal
- Inventory value calculation

### Admin Features

- User search and filtering
- User activation/deactivation
- Role management
- Order filtering and pagination
- Product archive management
- Promo code management
- Store statistics
- Revenue statistics
- Daily sales statistics
- Order status statistics
- Top-selling products
- Inventory monitoring

### Audit Logging

Admin and security-sensitive actions are recorded in the database.

Audit events include:

- User role changes
- User activation and deactivation
- User profile updates
- Product archiving and restoring
- Product restocking
- Manual stock adjustments
- Promo code updates

Audit logs support filtering and pagination.

## Security

The API includes:

- Argon2 password hashing
- JWT authentication
- Short-lived access tokens
- Refresh token rotation
- Database-backed refresh token sessions
- Access/refresh token type separation
- Refresh token revocation
- Role-based authorization
- Disabled-account protection
- Password-change session revocation
- Input validation with Pydantic
- Environment-based secrets
- Admin audit logging

Secrets are loaded from environment variables and are not stored in the repository.

## API Documentation

FastAPI automatically provides interactive API documentation.

After starting the application:

```text
http://localhost:8000/docs
```

OpenAPI schema:

```text
http://localhost:8000/openapi.json
```

The API is currently identified as:

```text
E-Commerce REST API
Version 1.0.0
```

## Health Check

The application provides a health endpoint that also checks PostgreSQL connectivity:

```http
GET /health
```

Example response:

```json
{
  "status": "ok",
  "database": "ok"
}
```

## Environment Variables

Create a `.env` file based on `.env.example`.

Example:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/shop_db
JWT_SECRET_KEY=YOUR_SECRET_KEY
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

Never commit the real `.env` file.

## Run with Docker

Make sure Docker Desktop is running.

Build and start the application:

```bash
docker compose up -d --build
```

Docker Compose starts:

- FastAPI application
- PostgreSQL database
- PostgreSQL test database

The API container automatically runs:

```bash
alembic upgrade head
```

before starting Uvicorn.

Check running containers:

```bash
docker compose ps
```

Check application health:

```text
http://localhost:8000/health
```

Swagger:

```text
http://localhost:8000/docs
```

Stop the containers:

```bash
docker compose down
```

## Local Development

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it and install dependencies:

```bash
pip install -r requirements.txt
```

Configure PostgreSQL and create `.env`.

Apply database migrations:

```bash
alembic upgrade head
```

Run the development server:

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## Database Migrations

Alembic is used to manage the PostgreSQL schema.

Apply all migrations:

```bash
alembic upgrade head
```

Check the current migration:

```bash
alembic current
```

Create a migration after changing SQLAlchemy models:

```bash
alembic revision --autogenerate -m "description"
```

## Testing

The project currently includes **250 automated API tests**.

Run the full test suite:

```bash
pytest -v
```

The tests cover authentication, authorization, products, categories, cart, orders, payments, refunds, promo codes, delivery, shipment tracking, inventory, admin features, audit logging and security behavior.

A separate PostgreSQL test database is available through Docker Compose.

## Continuous Integration

GitHub Actions automatically runs the automated test suite for repository changes.

The workflow verifies that the application remains stable before changes are merged or released.

## Project Structure

```text
.
├── alembic/
│   └── versions/
├── crud/
├── models/
├── routers/
├── schemas/
├── tests/
├── alembic.ini
├── auth.py
├── config.py
├── database.py
├── dependencies.py
├── docker-compose.yml
├── Dockerfile
├── main.py
├── requirements.txt
└── README.md
```

## Example API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/register` | Register a user |
| POST | `/login` | Login and receive access/refresh tokens |
| POST | `/refresh` | Rotate refresh token and issue new tokens |
| POST | `/logout` | Revoke refresh token |
| POST | `/logout-all` | Revoke all refresh sessions |
| GET | `/me` | Get current user |
| PATCH | `/me` | Update current user profile |
| PATCH | `/me/password` | Change password |
| GET | `/sessions` | List active refresh sessions |
| GET | `/products` | Search and list products |
| GET | `/products/{product_id}` | Get product |
| POST | `/products` | Create product |
| PUT | `/products/{product_id}` | Update product |
| DELETE | `/products/{product_id}` | Archive product |
| POST | `/products/{product_id}/restore` | Restore archived product |
| GET | `/cart` | Get shopping cart |
| POST | `/cart` | Add item to cart |
| POST | `/orders` | Create order |
| GET | `/orders` | Get current user's orders |
| GET | `/admin/orders` | Admin order management |
| GET | `/admin/inventory` | Admin inventory endpoints |
| GET | `/admin/audit-logs` | View audit log |
| GET | `/health` | Application/database health check |

The complete API specification is available through Swagger at `/docs`.

## CI Status

The repository uses GitHub Actions for continuous integration.

Current target release:

```text
v1.0.0
```

## License

This project was created as a backend development portfolio project.