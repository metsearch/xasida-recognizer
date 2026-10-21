PAYLOAD = {
    "aka_name": "Jeuzboul Mourid",
    "author": "Cheikh Ahmadou Bamba",
    "language": "ar",
}


def test_create_xasida(api_client):
    r = api_client.post("/xasidas", json=PAYLOAD)
    assert r.status_code == 201
    data = r.json()
    assert data["aka_name"] == PAYLOAD["aka_name"]
    assert "id" in data


def test_list_xasidas(api_client):
    api_client.post("/xasidas", json=PAYLOAD)
    api_client.post("/xasidas", json={**PAYLOAD, "aka_name": "Mawahiboul Mourid"})
    r = api_client.get("/xasidas")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_get_xasida(api_client):
    created = api_client.post("/xasidas", json=PAYLOAD).json()
    r = api_client.get(f"/xasidas/{created['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == created["id"]


def test_get_xasida_not_found(api_client):
    r = api_client.get("/xasidas/does-not-exist")
    assert r.status_code == 404


def test_delete_xasida(api_client):
    created = api_client.post("/xasidas", json=PAYLOAD).json()
    r = api_client.delete(f"/xasidas/{created['id']}")
    assert r.status_code == 204
    assert api_client.get(f"/xasidas/{created['id']}").status_code == 404
