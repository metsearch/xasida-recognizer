PAYLOAD = {"name": "Diwan Cheikh Ahmadou Bamba", "year": 1900}


def test_create_reference(api_client):
    r = api_client.post("/references", json=PAYLOAD)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == PAYLOAD["name"]
    assert "id" in data


def test_list_references(api_client):
    api_client.post("/references", json=PAYLOAD)
    api_client.post("/references", json={**PAYLOAD, "name": "Autre référence"})
    r = api_client.get("/references")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_get_reference(api_client):
    created = api_client.post("/references", json=PAYLOAD).json()
    r = api_client.get(f"/references/{created['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == created["id"]


def test_get_reference_not_found(api_client):
    r = api_client.get("/references/does-not-exist")
    assert r.status_code == 404


def test_delete_reference(api_client):
    created = api_client.post("/references", json=PAYLOAD).json()
    r = api_client.delete(f"/references/{created['id']}")
    assert r.status_code == 204
    assert api_client.get(f"/references/{created['id']}").status_code == 404
