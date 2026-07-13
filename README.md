# Trust Ledger

Trust Ledger is a Django REST Framework backend for account registration, KYC profiles, transactions, risk assessment, auditing, explanations, and webhooks.

## Local setup

Python 3.14 or newer is recommended for the current Django version.

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py runserver
```

Django does not automatically load `.env`. Set its values in your shell or deployment platform. The checked-in defaults are suitable only for local development.

## Verification

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

## Available account endpoints

- `POST /api/accounts/register/`
- `GET/PATCH /api/accounts/me/`
- `GET/POST/PATCH /api/accounts/kyc-profile/`
- `GET /api/accounts/kyc-status/`
