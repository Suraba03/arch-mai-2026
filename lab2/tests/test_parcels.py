def test_create_parcel_unauthorized(client):
    r = client.post("/parcels", json={"description": "Book", "weight_kg": 1.0})
    assert r.status_code == 401


def test_create_parcel_ok(client, auth_headers):
    r = client.post(
        "/parcels",
        json={"description": "Book", "weight_kg": 1.0},
        headers=auth_headers,
    )
    assert r.status_code == 201
    body = r.json()
    assert body["description"] == "Book"
    assert body["owner_id"] >= 1


def test_create_parcel_validation(client, auth_headers):
    r = client.post(
        "/parcels",
        json={"description": "", "weight_kg": -1},
        headers=auth_headers,
    )
    assert r.status_code == 422


def test_list_parcels(client, auth_headers, registered_user):
    client.post(
        "/parcels",
        json={"description": "Book", "weight_kg": 1.0},
        headers=auth_headers,
    )
    user_id = registered_user["id"]
    r = client.get(f"/users/{user_id}/parcels")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["description"] == "Book"


def test_list_parcels_user_404(client):
    r = client.get("/users/9999/parcels")
    assert r.status_code == 404