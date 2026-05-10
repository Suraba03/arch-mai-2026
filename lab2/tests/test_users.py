def test_get_by_login(client, registered_user):
    r = client.get("/users/by-login/ivan")
    assert r.status_code == 200
    assert r.json()["login"] == "ivan"


def test_get_by_login_404(client):
    r = client.get("/users/by-login/none")
    assert r.status_code == 404


def test_search_by_mask(client, registered_user, second_user):
    r = client.get("/users/search", params={"name": "iv"})
    assert r.status_code == 200
    logins = [u["login"] for u in r.json()]
    assert "ivan" in logins

    r = client.get("/users/search", params={"surname": "Petr"})
    assert r.status_code == 200
    assert any(u["last_name"].startswith("Petr") for u in r.json())


def test_search_requires_param(client):
    r = client.get("/users/search")
    assert r.status_code == 400