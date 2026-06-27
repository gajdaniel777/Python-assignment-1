def test_payment_cannot_exceed_remaining(client):
    invoice = _create_invoice(client)

    response = client.post(
        "/api/payments/record",
        json={
            "invoice_id": invoice["id"],
            "amount": "150.00",
            "currency": "USD",
            "status": "success",
            "provider_reference": "pay_001",
        },
    )
    assert response.status_code == 400
    assert "exceed" in response.json()["detail"].lower()


def test_failed_payment_does_not_increase_amount_paid(client):
    invoice = _create_invoice(client)

    response = client.post(
        "/api/payments/record",
        json={
            "invoice_id": invoice["id"],
            "amount": "40.00",
            "currency": "USD",
            "status": "failed",
            "provider_reference": "pay_fail_1",
            "failure_reason": "card_declined",
        },
    )
    assert response.status_code == 201
    assert response.json()["amount_paid"] == "0.00"
    assert response.json()["invoice_status"] == "issued"


def test_partial_and_full_payment_updates_status(client):
    invoice = _create_invoice(client)

    partial = client.post(
        "/api/payments/record",
        json={
            "invoice_id": invoice["id"],
            "amount": "40.00",
            "currency": "USD",
            "status": "success",
            "provider_reference": "pay_partial",
        },
    )
    assert partial.status_code == 201
    assert partial.json()["invoice_status"] == "partially_paid"
    assert partial.json()["amount_paid"] == "40.00"

    full = client.post(
        "/api/payments/record",
        json={
            "invoice_id": invoice["id"],
            "amount": "60.00",
            "currency": "USD",
            "status": "success",
            "provider_reference": "pay_full",
        },
    )
    assert full.status_code == 201
    assert full.json()["invoice_status"] == "paid"
    assert full.json()["amount_paid"] == "100.00"


def _create_invoice(client):
    plan = client.post(
        "/api/plans",
        json={"name": "Team", "price": "100.00", "currency": "USD"},
    ).json()
    customer = client.post(
        "/api/customers",
        json={"email": "dave@example.com", "name": "Dave"},
    ).json()
    subscription = client.post(
        "/api/subscriptions",
        json={"customer_id": customer["id"], "plan_id": plan["id"]},
    ).json()
    invoice = client.post(
        "/api/invoices/generate",
        json={"subscription_id": subscription["id"]},
    ).json()
    return invoice
