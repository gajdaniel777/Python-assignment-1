def test_customer_email_must_be_unique(client):
    payload = {"email": "alice@example.com", "name": "Alice"}
    first = client.post("/api/customers", json=payload)
    second = client.post("/api/customers", json=payload)
    assert first.status_code == 201
    assert second.status_code == 409
    assert "unique" in second.json()["detail"].lower()
