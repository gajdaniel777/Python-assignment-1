# SubLedger

This is my billing backend assignment project. It is a simple API (not a full Stripe clone) for managing:

- Plans
- Customers
- Subscriptions
- Invoices
- Payments
- Ledger entries (audit log)

I tried to keep the code easy to read. Business logic lives in **services**, database queries live in **repositories**, and the API routes just call the services.

Full design notes are in [DESIGN.md](DESIGN.md).

## What I used

- Python 3.12+
- FastAPI
- SQLAlchemy
- SQLite for local dev
- PostgreSQL with Docker (optional)
- pytest for tests

## How to run locally

```bash
cd subledger
python -m venv .venv
```

Windows:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open:

- API docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health
- Root (JSON): http://127.0.0.1:8000/

## Getting JSON responses with curl (Windows)

The API always returns JSON (`Content-Type: application/json`). On Windows PowerShell, `curl` is often an alias — use **`curl.exe`** instead:

```powershell
# Pretty-printed JSON
curl.exe -s http://127.0.0.1:8000/health | python -m json.tool

# Create a plan (note: use curl.exe and escaped quotes)
curl.exe -s -X POST http://127.0.0.1:8000/api/plans `
  -H "Content-Type: application/json" `
  -d '{\"name\":\"Pro\",\"price\":\"29.99\",\"billing_cycle\":\"monthly\",\"currency\":\"USD\"}' `
  | python -m json.tool
```

**Easier on Windows — use `Invoke-RestMethod`** (auto-parses JSON):

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health

Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/plans `
  -ContentType "application/json" `
  -Body '{"name":"Pro","price":"29.99","billing_cycle":"monthly","currency":"USD"}'
```

To pretty-print any object:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/plans | ConvertTo-Json -Depth 5
```

If you changed the database models, delete `subledger.db` and restart so tables are recreated.

## Docker

```bash
docker compose up --build
```

API runs on http://127.0.0.1:8001

## Run tests

```bash
pytest -v
```

There are 10 tests covering the main business rules from the assignment.

## API list (as required by assignment)

| Method | Endpoint | What it does |
|--------|----------|--------------|
| POST | `/api/plans` | Create a plan |
| GET | `/api/plans` | List plans |
| PATCH | `/api/plans/{id}` | Update plan or deactivate (`is_active: false`) |
| POST | `/api/customers` | Create customer |
| GET | `/api/customers` | List customers |
| GET | `/api/customers/{id}` | Get one customer |
| POST | `/api/subscriptions` | Create subscription |
| GET | `/api/subscriptions` | List subscriptions |
| PATCH | `/api/subscriptions/{id}/cancel` | Cancel subscription |
| POST | `/api/invoices/generate` | Generate invoice for active subscription |
| GET | `/api/invoices/{id}` | Get one invoice |
| POST | `/api/payments/record` | Record payment attempt |
| GET | `/api/customers/{id}/ledger` | Get customer ledger history |

## Quick example

1. Create a plan
2. Create a customer
3. Create a subscription
4. Generate invoice
5. Record payment

Use Swagger at `/docs` — easiest way to test.

## Assumptions I made

- No login/auth (kept it simple for the assignment)
- Subscription is **active** right after creation
- Invoice `amount_due` is taken from plan price at invoice generation time
- Ledger is append-only (no edit/delete)
- Payment status values are `success` and `failed`

## Limitations

- No real payment gateway (Stripe/Razorpay etc.)
- No tax, refunds, or proration
- No frontend UI
- No role-based access control

## Assignment checklist

| Requirement | Done? |
|-------------|-------|
| Layered structure (routes / services / repos / models / schemas) | Yes |
| All required API endpoints | Yes |
| All 8 business rules | Yes |
| DESIGN.md with ERD + tables + flows | Yes |
| 5+ tests | Yes (10 tests) |
| Dockerfile + docker-compose | Yes |
| Swagger docs | Yes (built into FastAPI) |
