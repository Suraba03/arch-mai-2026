def _create_parcel(client, headers):
    r = client.post(
        "/parcels",
        json={"description": "Box", "weight_kg": 2.0},
        headers=headers,
    )
    assert r.status_code == 201
    return r.json()


def test_create_delivery_ok(client, auth_headers, registered_user, second_user):
    parcel = _create_parcel(client, auth_headers)
    r = client.post(
        "/deliveries",
        json={"parcel_id": parcel["id"], "recipient_id": second_user["id"]},
        headers=auth_headers,
    )
    assert r.status_code == 201
    body = r.json()
    assert body["sender_id"] == registered_user["id"]
    assert body["recipient_id"] == second_user["id"]
    assert body["status"] == "created"


def test_create_delivery_unauthorized(client, second_user):
    r = client.post(
        "/deliveries",
        json={"parcel_id": 1, "recipient_id": second_user["id"]},
    )
    assert r.status_code == 401


def test_create_delivery_self(client, auth_headers, registered_user):
    parcel = _create_parcel(client, auth_headers)
    r = client.post(
        "/deliveries",
        json={"parcel_id": parcel["id"], "recipient_id": registered_user["id"]},
        headers=auth_headers,
    )
    assert r.status_code == 400


def test_create_delivery_recipient_not_found(client, auth_headers):
    parcel = _create_parcel(client, auth_headers)
    r = client.post(
        "/deliveries",
        json={"parcel_id": parcel["id"], "recipient_id": 9999},
        headers=auth_headers,
    )
    assert r.status_code == 404


def test_create_delivery_parcel_not_found(client, auth_headers, second_user):
    r = client.post(
        "/deliveries",
        json={"parcel_id": 9999, "recipient_id": second_user["id"]},
        headers=auth_headers,
    )
    assert r.status_code == 404


def test_create_delivery_alien_parcel(client, auth_headers, registered_user, second_user):
    # ivan1 (registered_user) создаёт посылку
    parcel = _create_parcel(client, auth_headers)

    # Логинимся как ivan2 и пытаемся отправить чужую посылку
    r = client.post(
        "/auth/login",
        data={"username": "masha", "password": "secret123"},
    )
    masha_headers = {"Authorization": f"Bearer {r.json()['access_token']}"}

    r = client.post(
        "/deliveries",
        json={"parcel_id": parcel["id"], "recipient_id": registered_user["id"]},
        headers=masha_headers,
    )
    assert r.status_code == 403


def test_get_deliveries_by_sender_recipient(
    client, auth_headers, registered_user, second_user
):
    parcel = _create_parcel(client, auth_headers)
    client.post(
        "/deliveries",
        json={"parcel_id": parcel["id"], "recipient_id": second_user["id"]},
        headers=auth_headers,
    )

    r = client.get(f"/deliveries/by-sender/{registered_user['id']}")
    assert r.status_code == 200
    assert len(r.json()) == 1

    r = client.get(f"/deliveries/by-recipient/{second_user['id']}")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_deliveries_user_404(client):
    assert client.get("/deliveries/by-sender/9999").status_code == 404
    assert client.get("/deliveries/by-recipient/9999").status_code == 404