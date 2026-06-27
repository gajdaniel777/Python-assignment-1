def _setup_subscription(client):
    plan = client.post(
        "/api/plans",
        json={"name": "Starter", "price": "50.00", "currency": "USD"},
    ).json()
    customer = client.post(
        "/api/customers",
        json={"email": "carol@example.com", "name": "Carol"},
    ).json()
    subscription = client.post(
        "/api/subscriptions",
        json={"customer_id": customer["id"], "plan_id": plan["id"]},
    ).json()
    return plan, customer, subscription


def test_invoice_amount_due_from_plan_price(client):
    plan, _, subscription = _setup_subscription(client)

    response = client.post(
        "/api/invoices/generate",
        json={"subscription_id": subscription["id"]},
    )
    assert response.status_code == 201
    invoice = response.json()
    assert invoice["amount_due"] == plan["price"]
    assert invoice["status"] == "issued"


def test_ledger_entry_on_invoice_created(client):
    _, customer, subscription = _setup_subscription(client)

    invoice = client.post(
        "/api/invoices/generate",
        json={"subscription_id": subscription["id"]},
    ).json()

    ledger = client.get(f"/api/customers/{customer['id']}/ledger")
    assert ledger.status_code == 200
    entries = ledger.json()
    assert len(entries) == 1
    assert entries[0]["entry_type"] == "invoice_created"
    assert entries[0]["invoice_id"] == invoice["id"]
