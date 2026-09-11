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

## API endpoints
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/register` | Register new user | No |
| POST | `/login` | Login and get JWT token | No |
| GET | `/me` | Get current user | Yes |
| GET | `/products` | Get products | No |
| GET | `/products/{product_id}` | Get product by ID | No |
| POST | `/products` | Create product | Yes |
| PUT | `/products/{product_id}` | Update product | Yes |
| DELETE | `/products/{product_id}` | Delete product | Admin |

## Search and pagination

Example:

```text
GET /products?search=Mouse&in_stock=true&skip=0&limit=10

The project currently includes 13 automated API tests.