# E-Commerce REST API

![Tests](https://github.com/zxnxgstu/fastapi-postgresql-crud/actions/workflows/tests.yml/badge.svg)

Production-style REST API for an e-commerce platform built with FastAPI, PostgreSQL, SQLAlchemy and JWT authentication.

The project includes authentication, role-based access control, product and inventory management, shopping cart, orders, payments, refunds, delivery tracking, promo codes, reviews, analytics, audit logging, Docker support, database migrations and automated CI testing.

## Live Demo

The API is deployed on Render and is publicly available.

**Swagger UI:**  
https://fastapi-postgresql-crud.onrender.com/docs

**Health Check:**  
https://fastapi-postgresql-crud.onrender.com/health

**Base URL:**  
https://fastapi-postgresql-crud.onrender.com

> The free Render instance may spin down after inactivity, so the first request can take longer than usual.

## Tech Stack

- Python 3.13
- FastAPI
- PostgreSQL 18
- SQLAlchemy 2
- Pydantic 2
- Alembic
- PyJWT
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
- Product price history
- Wishlist support
- Product reviews and ratings
- Price-drop notifications

### Shopping Cart and Orders

- User-specific shopping carts
- Add, update and remove cart items
- Order creation from cart
- Order history
- Order item price snapshots
- Subtotal, discount, delivery price and final total calculation
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
- Minimum order amount requirements
- Usage limits
- Usage counter
- Active/inactive state
- Admin promo code management

### Delivery and Shipment Tracking

- Saved user addresses
- Default delivery address
- Delivery methods
- Delivery pricing
- Delivery data snapshots in orders
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
- User activation and deactivation
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

Administrative and security-sensitive actions are recorded in the database.

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
- Pydantic input validation
- Environment-based secrets
- Admin audit logging

Secrets are loaded from environment variables and are not stored in the repository.

## API Documentation

### Live API

Swagger UI:

```text
https://fastapi-postgresql-crud.onrender.com/docs
```

Health check:

```text
https://fastapi-postgresql-crud.onrender.com/health
```

Base URL:

```text
https://fastapi-postgresql-crud.onrender.com
```

### Local Development

Swagger UI:

```text
http://localhost:8000/docs
```

OpenAPI schema:

```text
http://localhost:8000/openapi.json
```

The API is identified as:

```text
E-Commerce REST API
Version 1.0.0
```

## Health Check

The application provides a health endpoint that also validates PostgreSQL connectivity.

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

The API container automatically applies Alembic migrations before starting Uvicorn.

Check running containers:

```bash
docker compose ps
```

Check application health:

```text
http://localhost:8000/health
```

Open Swagger UI:

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

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create and configure `.env`.

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

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Database Migrations

Alembic is used to manage the PostgreSQL database schema.

Apply all migrations:

```bash
alembic upgrade head
```

Check the current migration:

```bash
alembic current
```

Check migration heads:

```bash
alembic heads
```

Create a new migration after changing SQLAlchemy models:

```bash
alembic revision --autogenerate -m "description"
```

## Testing

The project currently includes **250 automated API tests**.

Run the full test suite:

```bash
pytest -q
```

The tests cover:

- Authentication and JWT security
- User management
- Products and categories
- Shopping cart
- Orders
- Payments and refunds
- Promo codes
- Wishlist
- Reviews and ratings
- Delivery
- Shipment tracking
- Inventory
- Admin functionality
- Audit logging
- Health checks
- OpenAPI metadata

A separate PostgreSQL test database is available through Docker Compose.

## Continuous Integration

GitHub Actions automatically runs the test suite for repository changes.

The CI workflow verifies the application against PostgreSQL before changes are considered stable.

## Project Structure

```text
.
├── .github/
├── alembic/
│   └── versions/
├── crud/
├── models/
├── routers/
├── schemas/
├── tests/
├── .dockerignore
├── .env.example
├── .gitignore
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

| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | `/register` | Register a new user | Public |
| POST | `/login` | Login and receive JWT tokens | Public |
| POST | `/refresh` | Rotate refresh token | Public |
| POST | `/logout` | Revoke a refresh token | User |
| POST | `/logout-all` | Revoke all refresh sessions | User |
| GET | `/me` | Get current user profile | User |
| PATCH | `/me` | Update current user profile | User |
| GET | `/sessions` | List active refresh sessions | User |
| GET | `/products` | Search and list products | Public |
| GET | `/products/{product_id}` | Get a product | Public |
| POST | `/products` | Create a product | Authorized |
| PUT | `/products/{product_id}` | Update a product | Authorized |
| DELETE | `/products/{product_id}` | Archive a product | Admin |
| POST | `/products/{product_id}/restore` | Restore a product | Admin |
| GET | `/cart` | Get shopping cart | User |
| POST | `/cart` | Add product to cart | User |
| POST | `/orders` | Create an order | User |
| GET | `/orders` | Get current user's orders | User |
| GET | `/admin/orders` | Manage orders | Admin |
| GET | `/admin/audit-logs` | View audit logs | Admin |
| GET | `/health` | Check API and database health | Public |

The complete API specification is available through Swagger UI at `/docs`.

## Deployment

The production API is deployed on Render using Docker.

The deployment uses:

- Render Web Service
- Render PostgreSQL
- Docker
- Environment variables for secrets
- Automatic Alembic migrations during container startup
- `/health` as the Render health check endpoint
- Automatic deployment from the `main` branch

## Release

Stable release:

```text
v1.0.0
```

The project continues to receive deployment and documentation improvements after the initial release.

## Project Purpose

This project was created as a backend development portfolio project to demonstrate practical experience with FastAPI, PostgreSQL, authentication, database design, testing, Docker, CI/CD and deployment.