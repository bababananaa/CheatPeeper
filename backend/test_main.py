import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import get_db
from models import Base


# create separate temp database for testing
TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


# give every test a clean database and test client
@pytest.fixture
def client():
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


# 1201: successful user registration
def test_1201_register_user_successfully(client):
    response = client.post(
        "/users",
        json={
            "username": "student01",
            "email": "student01@example.com",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["username"] == "student01"
    assert data["email"] == "student01@example.com"
    assert data["role"] == "student"
    assert "password" not in data
    assert "password_hash" not in data


# 1202: retrieve existing user
def test_1202_retrieve_existing_user(client):
    registration = client.post(
        "/users",
        json={
            "username": "student02",
            "email": "student02@example.com",
            "password": "TestPassword123!",
        },
    )

    user_id = registration.json()["id"]

    response = client.get(f"/users/{user_id}")

    assert response.status_code == 200
    assert response.json()["id"] == user_id
    assert response.json()["username"] == "student02"
    assert response.json()["email"] == "student02@example.com"


# 1203: retrieve nonexistent user
def test_1203_nonexistent_user_returns_404(client):
    response = client.get("/users/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


# 1204: reject duplicate usernames and emails
def test_1204_duplicate_username_or_email_returns_409(client):
    original_user = {
        "username": "student03",
        "email": "student03@example.com",
        "password": "TestPassword123!",
    }

    first_response = client.post("/users", json=original_user)
    assert first_response.status_code == 201

    # try using the existing username with a different email
    duplicate_username = {
        "username": "student03",
        "email": "another@example.com",
        "password": "TestPassword123!",
    }

    response_username = client.post(
        "/users", json=duplicate_username
    )
    assert response_username.status_code == 409

    # try using a different username with the existing email
    duplicate_email = {
        "username": "student04",
        "email": "student03@example.com",
        "password": "TestPassword123!",
    }

    response_email = client.post("/users", json=duplicate_email)
    assert response_email.status_code == 409


# 1205: reject invalid email
def test_1205_invalid_email_returns_422(client):
    response = client.post(
        "/users",
        json={
            "username": "student05",
            "email": "not-an-email",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 422
