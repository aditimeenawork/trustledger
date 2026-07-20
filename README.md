# Trust Ledger

Trust Ledger is a backend platform for identity verification, transaction monitoring, explainable risk assessment, and compliance auditing. Built with Django and Django REST Framework, it combines deterministic risk rules, statistical anomaly detection, immutable audit records, structured explanations, asynchronous processing, and role-based access control in a modular API.

## Key capabilities

- Custom user accounts and KYC profiles
- Multipart KYC document upload with asynchronous mock verification
- User-scoped transaction creation and management
- Rule-based scoring and z-score anomaly detection
- Automatic transaction outcomes: `APPROVED`, `FLAGGED`, or `REJECTED`
- Immutable, append-only risk events and rule triggers
- Schema-validated, plain-English risk explanations
- Deterministic local explanation provider with optional Gemini integration
- Idempotent inbound gateway webhook processing
- Internal operational dashboard with aggregate platform metrics
- Group-based access for developers, compliance officers, and read-only auditors
- SQLite support for local development and PostgreSQL support for deployment

## Architecture

```text
Client / Gateway
       |
       v
Django REST API
       |
       +-- Accounts and KYC
       +-- Transactions ----> Celery risk evaluation
       |                            |
       |                            +-- Deterministic rules
       |                            +-- Statistical anomaly detection
       |                            +-- Immutable risk event
       |                            +-- Structured explanation
       +-- Audit and explanations
       +-- Idempotent webhooks
       +-- Internal dashboard
```

Celery tasks are dispatched after database commits where appropriate. Redis is used as the default broker and result backend. For lightweight local development and tests, tasks can be executed eagerly inside the Django process.

## Technology stack

| Area | Technology |
| --- | --- |
| Language | Python 3.14+ |
| Web framework | Django 6 |
| API framework | Django REST Framework |
| Background processing | Celery and Redis |
| Data analysis | NumPy |
| Explanation validation | JSON Schema |
| Optional AI provider | Google Gen AI (Gemini) |
| Development database | SQLite |
| Deployment database | PostgreSQL via psycopg |
| Testing | pytest, pytest-django, Factory Boy |

## Project structure

```text
trust_ledger/
|-- apps/
|   |-- accounts/       # Users, KYC profiles, roles, and permissions
|   |-- audit/          # Immutable risk events
|   |-- dashboard/      # Internal aggregate metrics
|   |-- explanations/   # Structured risk explanations
|   |-- kyc/            # KYC documents and verification tasks
|   |-- risk_engine/    # Risk rules, scoring, and anomaly detection
|   |-- transactions/   # Transaction API and orchestration
|   `-- webhooks/       # Idempotent gateway event handling
|-- config/             # Django, URL, WSGI, ASGI, and Celery configuration
|-- tests/              # Cross-application pytest suite
|-- .env.example        # Non-secret configuration template
|-- manage.py
`-- requirements.txt
```

## Local setup

### 1. Create and activate a virtual environment

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 2. Configure the environment

The application reads settings from environment variables and does not automatically load a `.env` file. Copy `.env.example` for reference, then export the required values in the shell or use your preferred environment loader.

```powershell
$env:DJANGO_SECRET_KEY = "replace-with-a-long-random-secret"
$env:DJANGO_DEBUG = "True"
$env:DJANGO_ALLOWED_HOSTS = "localhost,127.0.0.1"
$env:DATABASE_ENGINE = "sqlite"
$env:CELERY_TASK_ALWAYS_EAGER = "true"
$env:EXPLANATIONS_USE_MOCK_LLM = "true"
```

Never commit `.env` files, API keys, database files, private keys, uploaded KYC documents, or service-account credentials.

### 3. Initialize Django

```powershell
python manage.py migrate
python manage.py create_roles
python manage.py createsuperuser
```

`create_roles` creates the `Developer`, `ComplianceOfficer`, and `ReadOnlyAuditor` groups. Assign users to these groups through Django admin or the Django shell.

### 4. Start the application

For local development with eager Celery execution:

```powershell
$env:CELERY_TASK_ALWAYS_EAGER = "true"
python manage.py runserver
```

For asynchronous execution, start Redis, disable eager execution, and run a worker in a separate terminal:

```powershell
$env:CELERY_TASK_ALWAYS_EAGER = "false"
celery -A config worker --loglevel=info --pool=solo
```

The API is served at `http://127.0.0.1:8000/`, and Django admin is available at `http://127.0.0.1:8000/admin/`.

## Configuration reference

| Variable | Default | Purpose |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Development-only fallback | Django signing key; replace in every deployed environment |
| `DJANGO_DEBUG` | `True` | Enables Django debug mode |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated accepted hostnames |
| `DATABASE_ENGINE` | `sqlite` | Set to `postgres` to use PostgreSQL |
| `POSTGRES_DB` | `trustledger` | PostgreSQL database name |
| `POSTGRES_USER` | `trustledger` | PostgreSQL username |
| `POSTGRES_PASSWORD` | `trustledger` | PostgreSQL password |
| `POSTGRES_HOST` | `localhost` | PostgreSQL server hostname |
| `POSTGRES_PORT` | `5432` | PostgreSQL server port |
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | Celery broker URL |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/0` | Celery result backend |
| `CELERY_TASK_ALWAYS_EAGER` | `false` | Runs tasks synchronously when set to `true` |
| `EXPLANATIONS_USE_MOCK_LLM` | `true` | Uses deterministic local explanations when enabled |
| `GEMINI_API_KEY` | Not set | Gemini credential used when mock mode is disabled |
| `EXPLANATION_MODEL_NAME` | `gemini-3.5-flash` | Model requested from the explanation provider |

Production deployments must use a strong secret key, disable debug mode, configure explicit allowed hosts, provide secure PostgreSQL credentials, and protect all sensitive environment variables through a secrets manager.

## Authentication and authorization

The API supports Django session authentication and HTTP Basic authentication. Registration is public; protected endpoints require an authenticated user.

Authorization combines ownership rules with three project groups:

| Role | Intended access |
| --- | --- |
| `Developer` | Internal operational and diagnostic access |
| `ComplianceOfficer` | Compliance, transaction, audit, explanation, and dashboard access |
| `ReadOnlyAuditor` | Safe-method access to internal records without transaction mutations |

Regular users are scoped to their own transactions and KYC data. Internal audit, explanation, and dashboard endpoints require an internal role.

## API overview

### Accounts

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/accounts/register/` | Register a user |
| `GET`, `PUT`, `PATCH` | `/api/accounts/me/` | Retrieve or update the current user |
| `GET`, `POST`, `PATCH` | `/api/accounts/kyc-profile/` | Retrieve, submit, or update a KYC profile |
| `GET` | `/api/accounts/kyc-status/` | Retrieve the current KYC status |

### KYC documents

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/kyc/upload/` | Upload a KYC document as multipart form data |
| `GET` | `/api/kyc/documents/` | List the current user's KYC documents |

KYC uploads are rate-limited to five requests per hour. Verification currently uses deterministic mock extraction suitable for development and demonstration environments.

### Transactions

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET`, `POST` | `/api/transactions/` | List or create transactions |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/api/transactions/{id}/` | Retrieve, update, or delete a transaction |
| `GET` | `/api/transactions/{id}/risk/` | Retrieve the latest risk result and explanation |

New transactions begin in `PENDING`. Background evaluation updates them to `APPROVED`, `FLAGGED`, or `REJECTED`.

### Audit and explanations

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/audit/risk-events/{transaction_id}/` | Retrieve a transaction's complete risk-event history |
| `GET` | `/api/explanations/risk-events/{risk_event_id}/` | Retrieve or queue a structured explanation |

If an explanation has not yet been created, the explanation endpoint queues generation and returns `202 Accepted`.

### Dashboard

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/admin/dashboard/summary/` | Retrieve aggregate user, KYC, transaction, risk, explanation, and webhook metrics |

### Webhooks

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/webhooks/gateway/` | Accept and queue a gateway event |

Webhook requests require a unique `event_id`. Repeated IDs are acknowledged without duplicate processing. The endpoint is intentionally unauthenticated in the current implementation; production deployments should require gateway authentication or cryptographic signature verification.

## Risk evaluation

The deterministic engine evaluates the following rules:

| Rule | Severity | Trigger |
| --- | --- | --- |
| `VELOCITY_EXCEEDED` | High | More than five transactions within one hour |
| `AMOUNT_ABOVE_AVERAGE` | Medium | Amount exceeds ten times the user's average transaction amount |
| `KYC_NOT_VERIFIED` | High | KYC is missing or not verified |
| `KYC_TOO_RECENT` | Medium | KYC was verified less than two hours ago |
| `STATISTICAL_ANOMALY` | Medium | Absolute transaction amount z-score exceeds three after sufficient history |

Severity weights are `0.1` for low, `0.3` for medium, and `0.5` for high. Scores are capped at `1.0` and mapped as follows:

| Score | Tier | Transaction status |
| --- | --- | --- |
| `< 0.4` | Low | `APPROVED` |
| `>= 0.4` and `< 0.7` | Medium | `FLAGGED` |
| `>= 0.7` | High | `REJECTED` |

Every evaluation creates an immutable risk event. Re-evaluations reference the event they supersede, preserving the audit history. Rule triggers are also immutable.

## Explainable risk output

Each risk event can have one persisted explanation containing:

- A concise summary
- The assigned risk tier
- Up to five factual key factors
- An `APPROVE`, `MANUAL_REVIEW`, or `REJECT` recommendation

Provider output is validated against a strict JSON schema. Invalid output is retried with a correction prompt; repeated validation or provider failure produces a deterministic manual-review fallback.

## Testing and verification

Run the full pre-push verification sequence from the repository root:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python -m pytest --basetemp=.pytest_tmp -p no:cacheprovider
git diff --check
```

The pytest suite covers risk rules and scoring, audit immutability, explanation validation and fallback behavior, and webhook idempotency.

## Deployment notes

Before production deployment:

1. Set `DJANGO_DEBUG=False` and provide a strong `DJANGO_SECRET_KEY`.
2. Configure PostgreSQL and secure credentials outside the repository.
3. Run Redis and dedicated Celery workers.
4. Serve static and uploaded media through suitable infrastructure.
5. Add authentication or signature verification to the webhook endpoint.
6. Replace mock KYC verification with a trusted verification provider.
7. Review retention, encryption, observability, and access-control requirements for regulated data.

## Security

Do not report vulnerabilities through public issue discussions. Share security concerns privately with the project maintainers. Never include real identity documents, credentials, or production transaction data in bug reports or test fixtures.
