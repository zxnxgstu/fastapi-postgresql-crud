import os
from models import User
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from main import app, get_db


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5434/test_shop_db"
)

engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def auth_headers():
    client = TestClient(app)

    register_response = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/login",
        data={
            "username": "testuser",
            "password": "password123"
        }
    )

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }

@pytest.fixture
def admin_headers():
    client = TestClient(app)

    client.post(
        "/register",
        json={
            "username": "adminuser",
            "email": "admin@example.com",
            "password": "password123"
        }
    )

    db = TestingSessionLocal()

    user = (
        db.query(User)
        .filter(User.username == "adminuser")
        .first()
    )

    user.role = "admin"
    db.commit()
    db.close()

    login_response = client.post(
        "/login",
        data={
            "username": "adminuser",
            "password": "password123"
        }
    )

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }