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

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/products` | Get products |
| GET | `/products/{product_id}` | Get product by ID |
| POST | `/products` | Create product |
| PUT | `/products/{product_id}` | Update product |
| DELETE | `/products/{product_id}` | Delete product |

## Search and pagination

Example:

```text
GET /products?search=Mouse&in_stock=true&skip=0&limit=10