# Multi-Tenant Wallet API

A REST API built with **Django + Django REST Framework** for a wallet / ledger
service where multiple tenants (merchants or organizations) share the same
platform while their data stays fully isolated from one another.



**Live demo:** https://multi-tenant-wallet-api.vercel.app/swagger


## Trying It Out

A demo admin account is available on the live deployment for testing:
### Tenant A 
- **Username:** `admin`
- **Password:** `Admin@123`

A demo User account is available on the live deployment for testing:
### Tenant B
- **Username:** `sherlock`
- **Password:** `Admin@123`


---

## Tech Stack

- Django 6.1 + Django REST Framework
- PostgreSQL
- Djoser + Simple JWT (user auth / token issuing)
- drf-yasg (Swagger / ReDoc docs)
- Docker + docker-compose 
- Deployed on Vercel

## Core Features

- **Tenants** — create/list/retrieve/update/delete tenant records. Every
  tenant gets its own API key.
- **Users** — registered under a tenant via Djoser; login issues a JWT.
- **Wallets** — one wallet per user, scoped to the owning tenant.
- **Deposit / Withdraw** — balance changes, rejecting withdrawals that would
  overdraw the wallet.
- **Transfer** — moves funds between two wallets **of the same tenant** in
  a single atomic operation.
- **Transaction history** — paginated, per-wallet ledger.

## Multi-Tenancy

- Every request is resolved to a tenant via the `X-API-Key` header (matched
  against `Tenant.api_key`) together with the authenticated JWT user, whose
  `tenant` foreign key must match.
- All wallet, user, and transaction queries are filtered by
  `request.tenant`, so one tenant can never read or affect another tenant's
  data.
- Transfers validate that both the source and destination wallet belong to
  the same tenant; cross-tenant transfers are rejected.

## Ledger & Money Handling

- Balances are stored as `BigIntegerField` **integer minor units** (e.g.
  cents/paisa) — never floats — with a DB check constraint that balances
  can't go negative.
- Every balance change writes an **immutable `Transaction` row**
  (`DEPOSIT`, `WITHDRAWAL`, `TRANSFER_OUT`, `TRANSFER_IN`) with the
  resulting `balance_after`, so the ledger — not the wallet's `balance`
  field — is the source of truth.
- Transfers write a linked pair of `TRANSFER_OUT` / `TRANSFER_IN` rows
  sharing a `transfer_group_id`.
- Deposit, withdraw, and transfer all take a **client-supplied
  `idempotency_key`**, scoped per tenant (and per wallet pair, for
  transfers). A retried request with the same key returns the original
  stored response instead of double-applying the operation.
- Wallet rows are locked with `select_for_update()` inside a
  `transaction.atomic()` block before the balance is read or changed, so
  concurrent deposits/withdrawals/transfers on the same wallet(s) can't
  race each other. For transfers, both wallets are locked together in a
  fixed (sorted) order to avoid deadlocks.

## API Endpoints

| Area | Method | Endpoint | Purpose |
|---|---|---|---|
| Tenant | POST | `/api/tenants/` | Create tenant |
| Tenant | GET | `/api/tenants/` | List tenants |
| Tenant | GET | `/api/tenants/{id}/` | Retrieve tenant |
| Tenant | PUT/PATCH | `/api/tenants/{id}/` | Update tenant |
| Tenant | DELETE | `/api/tenants/{id}/` | Delete tenant |

| Auth | POST | `/api/auth/users/` | Register user under caller's tenant |
| Auth | POST | `/api/auth/jwt/create/` | Login — obtain access/refresh tokens |

| Wallet | POST | `/api/wallets/` | Create wallet (for the calling user) |
| Wallet | GET | `/api/wallets/` | List wallets (own, or all if staff) |
| Wallet | GET | `/api/wallets/{wallet_id}/` | Retrieve wallet |
| Wallet | POST | `/api/wallets/{wallet_id}/deposit/` | Deposit funds (idempotent) |
| Wallet | POST | `/api/wallets/{wallet_id}/withdraw/` | Withdraw funds (idempotent) |
| Wallet | GET | `/api/wallets/{wallet_id}/transactions/` | Paginated ledger history |
| Transfer | POST | `/api/transfers/` | Transfer between same-tenant wallets (idempotent) |
| Docs | GET | `/swagger/` | Swagger UI |
| Docs | GET | `/redoc/` | ReDoc |
| Admin | GET/POST | `/admin/` | Django admin |

Every endpoint (other than auth/docs/admin) expects an `X-API-Key` header
identifying the tenant, plus a `Bearer <access_token>` JWT for the
authenticated user.

## Running Locally

### With Docker (recommended)

```bash
git clone https://github.com/ashrafulX/Multi-Tenant-Wallet-API.git
cd Multi-Tenant-Wallet-API
cp .env.example .env   # fill in SECRET_KEY and DB_* values
docker-compose up --build
```

The API will be available at `http://127.0.0.1:8000/api/`.

Run migrations and create a superuser in a second terminal if needed:

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### Without Docker

```bash
git clone https://github.com/ashrafulX/Multi-Tenant-Wallet-API.git
cd Multi-Tenant-Wallet-API
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in SECRET_KEY and DB_* values (PostgreSQL)
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Environment Variables (`.env`)

```
SECRET_KEY=your-django-secret-key
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

Generate a `SECRET_KEY` with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```


Typical flow:

1. `POST /api/tenants/` to create a tenant — note the returned `api_key`.
2. `POST /api/auth/users/` (with `X-API-Key` set) to register a user under
   that tenant.
3. `POST /api/auth/jwt/create/` to log in and get an access token.
4. `POST /api/wallets/` (with `X-API-Key` + `Authorization: Bearer …`) to
   create a wallet for that user.
5. Deposit / withdraw / transfer / view transaction history using the
   endpoints above.

## Running Tests

```bash
python manage.py test
```

Tests cover the core flows per app (`tenants`, `accounts`, `wallets`,
`ledger`): insufficient funds on withdrawal, duplicate idempotency keys,
concurrent transfer locking, and cross-tenant access being blocked.

## Assumptions & Trade-offs

- Each user has at most one wallet (`Wallet.owner` is a `OneToOneField`).
- Tenant identity is resolved from the `X-API-Key` header rather than a
  subdomain or path prefix, for simplicity.
- Idempotency keys are scoped per tenant + operation type; for transfers,
  the key is additionally checked against a fingerprint of
  `(from_wallet, to_wallet, amount)` so the same key can't silently be
  reused for a different transfer.
- Given the ~4–5 hour scope, this favors correctness of the core
  money-movement logic (locking, atomicity, ledger-as-source-of-truth,
  idempotency) over production concerns like rate limiting, refresh-token
  rotation/blacklisting, or fine-grained permissions beyond tenant/owner
  checks.