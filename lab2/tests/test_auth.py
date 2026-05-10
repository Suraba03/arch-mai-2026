def test_register_and_login(client):
    r = client.post(
        "/auth/register",
        json={"login": "ivan", "password": "secret123",
              "first_name": "Ivan", "last_name": "Petrov"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["login"] == "ivan"
    assert "password" not in body and "password_hash" not in body

    r = client.post(
        "/auth/login",
        data={"username": "ivan", "password": "secret123"},
    )
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert token


def test_register_duplicate(client, registered_user):
    r = client.post(
        "/auth/register",
        json={"login": "ivan", "password": "x123456",
              "first_name": "X", "last_name": "Y"},
    )
    assert r.status_code == 409


def test_login_invalid_password(client, registered_user):
    r = client.post(
        "/auth/login",
        data={"username": "ivan", "password": "wrong"},
    )
    assert r.status_code == 401


def test_register_validation_error(client):
    r = client.post(
        "/auth/register",
        json={"login": "x", "password": "x",
              "first_name": "", "last_name": ""},
    )
    assert r.status_code == 422