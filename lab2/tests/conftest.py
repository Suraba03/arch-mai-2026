import pytest
from fastapi.testclient import TestClient

from app.main import app
from app import storage


@pytest.fixture(autouse=True)
def _reset_storage():
    """Перед каждым тестом обнуляем in-memory хранилище."""
    storage.reset_storage()
    yield


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def registered_user(client: TestClient):
    payload = {
        "login": "ivan",
        "password": "secret123",
        "first_name": "Ivan",
        "last_name": "Petrov",
    }
    r = client.post("/auth/register", json=payload)
    assert r.status_code == 201, r.text
    return r.json()


@pytest.fixture()
def second_user(client: TestClient):
    payload = {
        "login": "masha",
        "password": "secret123",
        "first_name": "Masha",
        "last_name": "Sidorova",
    }
    r = client.post("/auth/register", json=payload)
    assert r.status_code == 201, r.text
    return r.json()


@pytest.fixture()
def auth_headers(client: TestClient, registered_user):
    r = client.post(
        "/auth/login",
        data={"username": "ivan", "password": "secret123"},
    )
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}