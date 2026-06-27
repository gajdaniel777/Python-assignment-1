def test_cannot_subscribe_to_inactive_plan(client):
    plan = _create_plan(client)
    client.patch(f"/api/plans/{plan['id']}", json={"is_active": False})
    customer = _create_customer(client)

    response = client.post(
        "/api/subscriptions",
        json={"customer_id": customer["id"], "plan_id": plan["id"]},
    )
    assert response.status_code == 400
    assert "inactive plan" in response.json()["detail"].lower()


def test_no_duplicate_active_subscription_same_plan(client):
    plan = _create_plan(client)
    customer = _create_customer(client)
    payload = {"customer_id": customer["id"], "plan_id": plan["id"]}

    first = client.post("/api/subscriptions", json=payload)
    second = client.post("/api/subscriptions", json=payload)

    assert first.status_code == 201
    assert second.status_code == 400
    assert "two active subscriptions" in second.json()["detail"].lower()


def _create_plan(client, price="19.99"):
    return client.post(
        "/api/plans",
        json={"name": "Basic", "price": price, "currency": "USD"},
    ).json()


def _create_customer(client, email="bob@example.com"):
    return client.post(
        "/api/customers",
        json={"email": email, "name": "Bob"},
    ).json()
