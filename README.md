# Trust Ledger

Trust Ledger is a Django REST Framework backend for user accounts, KYC document management, transactions, asynchronous risk assessment, and immutable risk-event auditing.

## Features

- Custom user accounts and KYC profiles
- KYC document upload and verification workflow
- User-scoped transaction management
- Asynchronous transaction evaluation with Celery and Redis
- Rule-based and statistical anomaly detection
- Append-only risk events with rule-trigger details
- Staff access to all transactions and audit histories through the API and Django admin

## Technology

- Python 3.14+
- Django 6
- Django REST Framework
- Celery with Redis
- NumPy
- SQLite for local development

## Local setup

Create a virtual environment and install the dependencies:

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Apply the database migrations and optionally create an administrator:

```powershell
python manage.py migrate
python manage.py createsuperuser
```

The application reads configuration from environment variables. Copy `.env.example` as a reference, but note that Django does not load `.env` files automatically:

```powershell
Copy-Item .env.example .env
$env:DJANGO_SECRET_KEY = "replace-with-a-long-random-secret"
$env:DJANGO_DEBUG = "True"
$env:DJANGO_ALLOWED_HOSTS = "localhost,127.0.0.1"
$env:CELERY_BROKER_URL = "redis://localhost:6379/0"
$env:CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
```

## Running locally

Start a Redis server, then run Django and Celery in separate terminals.

API server:

```powershell
.\env\Scripts\Activate.ps1
python manage.py runserver
```

Celery worker on Windows:

```powershell
.\env\Scripts\Activate.ps1
celery -A config worker --loglevel=info --pool=solo
```

New transactions are created with a `PENDING` status. The Celery worker evaluates each transaction and changes its status to `APPROVED`, `FLAGGED`, or `REJECTED`.

## Configuration

| Variable | Default | Description |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Development-only fallback | Django cryptographic signing key |
| `DJANGO_DEBUG` | `True` | Enables or disables debug mode |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated allowed host names |
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | Celery message broker |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/0` | Celery task result backend |

The checked-in defaults are intended only for local development. Set a strong secret key and disable debug mode in production.

## Authentication

The API supports session and basic authentication. Registration is public; the remaining API endpoints require an authenticated user. Regular users can access only their own transactions, documents, and risk histories. Staff users can access all transactions and risk-event histories.

## API endpoints

### Accounts

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/accounts/register/` | Register a user |
| `GET`, `PATCH`, `PUT` | `/api/accounts/me/` | Retrieve or update the authenticated user |
| `GET`, `POST`, `PATCH` | `/api/accounts/kyc-profile/` | Retrieve, submit, or update the user's KYC profile |
| `GET` | `/api/accounts/kyc-status/` | Retrieve the user's KYC status |

### KYC documents

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/kyc/upload/` | Upload a KYC document using multipart form data |
| `GET` | `/api/kyc/documents/` | List the authenticated user's KYC documents |

### Transactions

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET`, `POST` | `/api/transactions/` | List or create transactions |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/api/transactions/{id}/` | Retrieve, update, or delete a transaction |
| `GET` | `/api/transactions/{id}/risk/` | Retrieve the latest risk result for a transaction |

### Audit

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/audit/risk-events/{transaction_id}/` | List a transaction's complete risk-event history and triggered rules |

The Django administration interface is available at `/admin/`.

## Risk evaluation

The risk engine currently evaluates four rules:

| Rule code | Severity | Trigger |
| --- | --- | --- |
| `VELOCITY_EXCEEDED` | High | More than five transactions within one hour |
| `AMOUNT_ABOVE_AVERAGE` | Medium | Amount exceeds ten times the user's average transaction amount |
| `KYC_NOT_VERIFIED` | High | The user does not have verified KYC |
| `KYC_TOO_RECENT` | Medium | KYC was verified less than two hours ago |

After at least five previous transactions, the engine also checks whether the current amount has an absolute z-score greater than three. A detected statistical anomaly adds a medium-severity `STATISTICAL_ANOMALY` trigger.

Severity weights are `0.1` for low, `0.3` for medium, and `0.5` for high. The total score is capped at `1.0` and mapped to a tier and transaction status:

| Risk score | Tier | Transaction status |
| --- | --- | --- |
| Less than `0.4` | Low | `APPROVED` |
| `0.4` to less than `0.7` | Medium | `FLAGGED` |
| `0.7` or greater | High | `REJECTED` |

Every evaluation creates a new immutable risk event. Re-evaluations link to the previous event through `supersedes`, preserving the transaction's audit history.

## Verification

Run the project checks before committing changes:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
git diff --check
```
