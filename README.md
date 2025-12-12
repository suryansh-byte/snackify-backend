SNACKIFY Backend - Local Setup

Overview
- Flask backend for Snackify. This README explains how to run the backend locally for integration with the Flutter frontend.

Prerequisites
- Python 3.8+ installed.
- (Optional) Postgres if you want production parity. By default the app will use SQLite for quick testing.

Quick local start (PowerShell)

```powershell
cd 'C:\Users\KIIT\New folder\SNACKIFY'
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Use the default sqlite DB or set DATABASE_URL to a Postgres URL
$env:DATABASE_URL = 'sqlite:///snackify.db'
python app.py
```

Notes
- The app exposes a health endpoint at `GET /health`.
- Authentication endpoints:
  - `POST /api/auth/register` {username, password}
  - `POST /api/auth/login` {username, password} -> returns JWT token
- Order endpoints require an `Authorization: Bearer <token>` header.

Flutter integration hints
- Android emulator: use `http://10.0.2.2:5000` as base URL.
- iOS simulator: use `http://127.0.0.1:5000`.
- Real device: use your machine IP (e.g. `http://192.168.1.100:5000`) and ensure firewall allows connections.
- Ensure you add `http` package to `pubspec.yaml` and set the base URL accordingly.

Example quick tests (PowerShell)

```powershell
# Register
Invoke-RestMethod -Uri http://127.0.0.1:5000/api/auth/register -Method POST -Body (@{username='testuser'; password='pass123'} | ConvertTo-Json) -ContentType 'application/json'

# Login
Invoke-RestMethod -Uri http://127.0.0.1:5000/api/auth/login -Method POST -Body (@{username='testuser'; password='pass123'} | ConvertTo-Json) -ContentType 'application/json'
```
