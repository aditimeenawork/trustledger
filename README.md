# Trust Ledger

Trust Ledger is a Django REST Framework backend for user accounts, KYC document management, transactions, risk assessment, immutable risk-event auditing, structured risk explanations, and inbound gateway webhooks.

## Features

- Custom user accounts and KYC profiles
- KYC document upload and verification workflow
- User-scoped transaction management
- Asynchronous transaction evaluation with Celery and Redis
- Rule-based and statistical anomaly detection
- Append-only risk events with rule-trigger details
- Schema-validated, plain-English risk explanations with a local mock provider and optional Gemini integration
- Idempotent inbound webhook capture and processing
- Staff access to all transactions and audit histories through the API and Django admin

## Technology

- Python 3.14+
- Django 6
- Django REST Framework
- Celery with Redis
- NumPy
- Google Gen AI and JSON Schema
- SQLite for local development, with a PostgreSQL driver included for deployment integrations

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
$env:GEMINI_API_KEY = "replace-with-your-api-key"
$env:EXPLANATION_MODEL_NAME = "gemini-3.5-flash"
```

Never commit `.env`, API keys, database files, private keys, or service-account credentials. The repository tracks `.env.example` only, and every value in it is a non-secret placeholder.

## Running locally

The current development settings execute Celery tasks eagerly in the Django process, so Redis and a separate worker are not required for local requests. To use queued task execution, disable Celery eager mode in the settings and start Redis plus a worker.

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

New transactions are created with a `PENDING` status. The risk-evaluation task changes each transaction's status to `APPROVED`, `FLAGGED`, or `REJECTED`.

Risk explanations use the deterministic mock provider by default. The Gemini API key is only required after mock mode is disabled in the Django settings.

## Configuration

| Variable | Default | Description |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Development-only fallback | Django cryptographic signing key |
| `DJANGO_DEBUG` | `True` | Enables or disables debug mode |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated allowed host names |
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | Celery message broker |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/0` | Celery task result backend |
| `GEMINI_API_KEY` | Not set | Gemini credential used when mock explanation generation is disabled |
| `EXPLANATION_MODEL_NAME` | `gemini-3.5-flash` | Model requested for generated explanations |

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

### Explanations

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/explanations/risk-events/{risk_event_id}/` | Return a stored explanation, or queue generation and return `202 Accepted` |

Explanation responses contain a validated summary, risk tier, up to five key factors, and a recommendation. Non-staff users can request explanations only for their own transactions.

### Webhooks

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/webhooks/gateway/` | Accept a gateway event and queue it for processing |

Webhook requests require a unique `event_id`; repeated IDs are acknowledged without being processed twice. The endpoint currently allows unauthenticated requests, so production deployments should place it behind gateway authentication or signature verification.

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

After a risk event is created, the application generates and stores one structured explanation for it. Invalid provider output falls back to a manual-review explanation.

## Verification

Run the project checks before committing changes:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
pytest
git diff --check
```
