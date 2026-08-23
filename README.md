# ITCAFinanceBack

The brain of [ITCA Account Management](https://github.com/Ebrima-etech/ITCAFinanceWeb) — a Django + Django REST Framework API that tracks ITCA's dues, event revenue and costs, gifts, budget, and everything going out, with a full activity log of who did what.

Companion frontend: [ITCAFinanceWeb](https://github.com/Ebrima-etech/ITCAFinanceWeb).

## Stack

- Django 5 + Django REST Framework
- PostgreSQL
- JWT auth (`djangorestframework-simplejwt`)
- camelCase JSON in/out (`djangorestframework-camel-case`), so the API speaks the same field names as the frontend

## Setup

```bash
docker compose up -d          # from the parent ITCA/ folder — starts Postgres
python -m venv venv
venv\Scripts\activate         # Windows
pip install -r requirements.txt
copy .env.example .env        # then edit SECRET_KEY, SEED_ADMIN_PASSWORD, etc.
python manage.py migrate
python manage.py seed_admin   # creates the first admin login from .env
python manage.py runserver 4000
```

API is served at `http://localhost:4000/api`.

## App layout

Each Django app owns one job:

| App | Owns |
|---|---|
| `accounts` | users, login, roles (Admin / Finance Officer / Committee Member), permission classes shared by every other app |
| `activitylog` | the one shared `record_activity()` helper every write calls |
| `ledger` | `transactions` — the table everything else calculates from |
| `events` | events, linked transactions, profit/loss, CSV ticketing import |
| `dues` | membership dues (cash + online), each wrapping a `DUE` transaction |
| `budget` | `budget_items`, budget-vs-actual (computed live, never stored) |
| `dashboard` | read-only aggregation over the ledger and events |
| `reports` | CSV export |
| `receipts` | future — schema only, not wired to any view yet |

## Design notes

- Money is `Decimal`, never a float.
- Deletes are soft (`deleted_at` flags) — nothing money-related is ever hard-deleted.
- Routing is deliberately slash-free (`APPEND_SLASH = False`) to match how the frontend calls the API.
