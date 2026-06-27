def test_plan_price_must_be_positive(client):
    response = client.post("/api/plans", json={"name": "Free", "price": "0"})
    assert response.status_code == 422


def test_create_plan_success(client):
    response = client.post(
        "/api/plans",
        json={"name": "Pro", "price": "29.99", "currency": "USD", "billing_interval": "monthly"},
    )
    assert response.status_code == 201
    assert response.json()["price"] == "29.99"
    assert response.json()["is_active"] is True
