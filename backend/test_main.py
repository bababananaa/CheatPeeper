import os
import tempfile

# point the app at a throwaway SQLite db before anything loads backend/.env
# (load_dotenv doesn't override variables that are already set)
os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(tempfile.mkdtemp(), "test.db")
os.environ["JWT_SECRET_KEY"] = "test-secret-key-that-is-long-enough-for-hs256"

import pytest
from fastapi.testclient import TestClient

import mailer
from database import engine
from main import app
from models import Base

client = TestClient(app)

USER = {"username": "ava", "email": "ava@ufl.edu", "password": "password123"}

# latest verification code "emailed" to each address
sent_codes = {}


# fresh empty tables for every test, and catch codes instead of emailing them
@pytest.fixture(autouse=True)
def setup(monkeypatch):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    sent_codes.clear()
    monkeypatch.setattr(mailer, "send_verification_email", lambda to, code: sent_codes.update({to: code}))


def signup_and_verify():
    client.post("/users", json=USER)
    client.post("/auth/verify-email", json={"email": USER["email"], "code": sent_codes[USER["email"]]})


# signs up, verifies, logs in, returns the header for protected routes
def auth_header():
    signup_and_verify()
    token = client.post("/auth/login", data=USER).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_home():
    assert client.get("/").status_code == 200


def test_health():
    assert client.get("/health").status_code == 200


@pytest.mark.skipif(engine.dialect.name != "postgresql", reason="uses a Postgres-only query")
def test_db_check():
    assert client.get("/db-check").status_code == 200


def test_create_user():
    assert client.post("/users", json=USER).status_code == 201


def test_verify_email():
    client.post("/users", json=USER)
    response = client.post("/auth/verify-email", json={"email": USER["email"], "code": sent_codes[USER["email"]]})
    assert response.status_code == 200


def test_resend_code():
    client.post("/users", json=USER)
    assert client.post("/auth/resend-code", json={"email": USER["email"]}).status_code == 200


def test_login():
    signup_and_verify()
    # login takes form data, not JSON
    assert client.post("/auth/login", data=USER).status_code == 200


def test_get_me():
    assert client.get("/users/me", headers=auth_header()).status_code == 200


def test_get_user():
    assert client.get("/users/1", headers=auth_header()).status_code == 200
