# Eco-Chain Backend

REST API for the **Eco-Chain** regenerative living platform — built with Django 5 + Django REST Framework.

> **Frontend developers:** Follow [Quick Start](#quick-start) to get the API running locally in under 5 minutes. Then open **[Swagger UI](http://127.0.0.1:8000/api/docs/)** to explore and test every endpoint interactively.

---

## Table of Contents

- [Live API Docs (Swagger)](#live-api-docs-swagger)
- [Quick Start](#quick-start)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Frontend Integration](#frontend-integration)
- [Docker Setup](#docker-setup-optional)
- [Troubleshooting](#troubleshooting)
- [Production Checklist](#production-checklist)

---

## Live API Docs (Swagger)

Once the server is running, open your browser:

| URL | What it is |
|-----|------------|
| `http://127.0.0.1:8000/api/docs/` | **Swagger UI** — interactive docs, try every endpoint from the browser |
| `http://127.0.0.1:8000/api/redoc/` | ReDoc — clean reference-style docs |
| `http://127.0.0.1:8000/api/schema/` | Raw OpenAPI 3 schema (YAML) — use to generate client SDKs |

### How to authenticate in Swagger UI

1. Call **POST /api/v1/auth/signup/** → grab the OTP from the terminal → call **POST /api/v1/auth/verify/**
2. Copy the `access` token from the response
3. Click the green **Authorize** button at the top of Swagger UI
4. Paste your token — no `Bearer` prefix needed, Swagger adds it automatically
5. All authenticated endpoints now work via "Try it out"

---

## Quick Start

### Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.11+ | 3.13 works — see note below |
| PostgreSQL | 14+ | Optional — falls back to SQLite if not configured |
| Redis / Memurai | 6+ | Optional — falls back to in-memory cache if not configured |

> **Windows users:** Install [Memurai](https://www.memurai.com/get-memurai) for Redis — it runs as a Windows service on port 6379 automatically.

> **Python 3.13 users:** The pinned versions of `Pillow` and `psycopg2-binary` in `requirements.txt` don't have wheels for Python 3.13. Before running `pip install`, upgrade them:
> ```bash
> pip install Pillow==10.4.0 psycopg2-binary==2.9.12 --only-binary=:all:
> ```
> Then update those two lines in `requirements.txt` to match before continuing.

---

### 1. Clone the repo

```bash
git clone https://github.com/your-org/eco_chain.git
cd eco_chain
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your `.env` file

```bash
cp .env.example .env
```

Open `.env` and set at minimum:

```env
SECRET_KEY=any-long-random-string-here
```

Leave `DB_NAME` and `REDIS_URL` blank to use SQLite + in-memory cache (fine for local dev).

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Seed the plant catalogue

```bash
python manage.py seed_plants
# → Seeded 8 new plant(s). Total catalogue: 8.
```

### 7. Start the server

```bash
python manage.py runserver
```

The API is live at **http://127.0.0.1:8000**. Open **http://127.0.0.1:8000/api/docs/** to explore it.

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the values you need.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | — | Django secret key — generate one with `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DEBUG` | No | `True` | Set to `False` in production |
| `ALLOWED_HOSTS` | No | `*` | Comma-separated list of allowed hosts |
| `DB_NAME` | No | — | PostgreSQL database name. If blank, falls back to SQLite |
| `DB_USER` | No | `postgres` | PostgreSQL user |
| `DB_PASSWORD` | No | — | PostgreSQL password |
| `DB_HOST` | No | `127.0.0.1` | PostgreSQL host |
| `DB_PORT` | No | `5432` | PostgreSQL port |
| `REDIS_URL` | No | — | e.g. `redis://127.0.0.1:6379/1`. If blank, falls back to in-memory cache |
| `SENDGRID_API_KEY` | No | — | If blank, OTPs print to the terminal instead of being emailed |
| `GOOGLE_MAPS_KEY` | No | — | If blank, falls back to free Nominatim geocoder |

---

## API Reference

All endpoints are under `/api/v1/`. Full interactive docs at `/api/docs/`.

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/signup/` | None | Create account, send OTP |
| POST | `/auth/verify/` | None | Verify OTP → returns JWT tokens |
| POST | `/auth/resend-otp/` | None | Resend OTP |
| POST | `/auth/login/` | None | Email + password → JWT tokens |
| POST | `/auth/refresh/` | Refresh token | Get a new access token |
| GET | `/dashboard/` | JWT | Home screen payload (user + plants + tasks + impact) |
| POST | `/green-match/` | JWT | Recommend plants for a plot |
| GET | `/user/plants/` | JWT | List user's garden |
| POST | `/user/plants/` | JWT | Add a plant to user's garden |
| GET | `/plants/<uuid>/` | JWT | Plant detail |

### Authentication flow

```
signup → [check terminal for OTP] → verify → receive access + refresh tokens
                                                        ↓
                                     attach access token to all requests
                                     Authorization: Bearer <access_token>
                                                        ↓
                                     refresh when expired (1 hour TTL)
```

### Example: Sign Up → Verify → Dashboard

**1. Sign Up**
```http
POST /api/v1/auth/signup/
Content-Type: application/json

{
  "name": "Amara Okafor",
  "email": "amara@example.com",
  "password": "StrongPass!23",
  "location": "Lagos, Nigeria"
}
```
Response `201`: `{ "detail": "Account created. Check your email for your OTP." }`

In dev (no SendGrid key), the OTP prints to the Django terminal:
```
Your Eco-Chain verification code is: 721559
```

**2. Verify OTP**
```http
POST /api/v1/auth/verify/
Content-Type: application/json

{
  "email": "amara@example.com",
  "otp": "721559"
}
```
Response `200`:
```json
{
  "access": "eyJhbGciOiJIUzI1NiIs...",
  "refresh": "eyJhbGciOiJIUzI1NiIs...",
  "user": { "id": "...", "name": "Amara Okafor", "email": "amara@example.com" }
}
```

**3. Dashboard**
```http
GET /api/v1/dashboard/
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```
Response `200`:
```json
{
  "user": { ... },
  "plants": [],
  "upcomingTasks": [],
  "impactStats": { "waterSavedLitres": 0.0, "co2OffsetKg": 0.0 }
}
```

---

## Frontend Integration

### Flutter (mobile)

```dart
final dio = Dio(BaseOptions(baseUrl: 'http://10.0.2.2:8000/api/v1/'));
// 10.0.2.2 = Android emulator loopback to host machine
// iOS simulator: use http://127.0.0.1:8000/api/v1/

// After login/verify, store tokens securely
await storage.write(key: 'access', value: response.data['access']);
await storage.write(key: 'refresh', value: response.data['refresh']);

// Attach token to every request via interceptor
dio.interceptors.add(InterceptorsWrapper(
  onRequest: (options, handler) async {
    final token = await storage.read(key: 'access');
    if (token != null) options.headers['Authorization'] = 'Bearer $token';
    return handler.next(options);
  },
));
```

### Next.js (web)

```ts
// app/api/login/route.ts
import { cookies } from 'next/headers';

export async function POST(req: Request) {
  const body = await req.json();
  const res = await fetch(`${process.env.API_URL}/api/v1/auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  cookies().set('access', data.access, { httpOnly: true, secure: true, sameSite: 'strict' });
  cookies().set('refresh', data.refresh, { httpOnly: true, secure: true, sameSite: 'strict' });
  return Response.json({ user: data.user });
}
```

In `.env.local`: `API_URL=http://localhost:8000`

CORS is pre-configured for `http://localhost:3000`. For other origins, add them to `CORS_ALLOWED_ORIGINS` in your `.env`.

---

## Docker Setup (optional)

If you have Docker installed, this brings up PostgreSQL, Redis, and Django in one command:

```bash
cp .env.example .env
# In .env, set: DB_HOST=db and REDIS_URL=redis://redis:6379/1

docker compose up --build
```

Migrations and seeding run automatically.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'environ'` | Make sure your venv is activated and run `pip install -r requirements.txt` |
| `relation "..." does not exist` | Run `python manage.py migrate` |
| `database "eco_chain" does not exist` | Create it: `psql -U postgres -c "CREATE DATABASE eco_chain;"` |
| `password authentication failed for user "postgres"` | Check `DB_PASSWORD` in your `.env` matches your PostgreSQL password |
| Redis connection refused (port 6379) | Start Memurai (Windows) or run `sudo service redis-server start` (Linux/WSL) |
| `Pillow` or `psycopg2-binary` build fails | You're on Python 3.13 — see the note in [Quick Start](#quick-start) |
| OTP email not arriving | Expected in dev — check the Django terminal for the OTP code |
| `401 Unauthorized` on protected endpoints | Access token expired (1h TTL) — call `POST /auth/refresh/` |
| `climate_zone: "unknown"` from Green Match | No `GOOGLE_MAPS_KEY` set or location not in bounding-box table — scoring still works |
| CORS error from Flutter web / Next.js | Add your origin to `CORS_ALLOWED_ORIGINS` in `.env` |

---

## Production Checklist

- [ ] `DEBUG=False` in `.env`
- [ ] Strong `SECRET_KEY` — generate with `python -c "import secrets; print(secrets.token_urlsafe(50))"`
- [ ] `ALLOWED_HOSTS` set to your real domain
- [ ] Real `DATABASE_URL` pointing to managed PostgreSQL
- [ ] Real `REDIS_URL` pointing to managed Redis
- [ ] `SENDGRID_API_KEY` set for OTP emails
- [ ] `GOOGLE_MAPS_KEY` set for accurate geocoding
- [ ] `python manage.py collectstatic` run (Dockerfile handles this automatically)
- [ ] Nginx in front of Gunicorn for TLS termination
- [ ] Monitor auth endpoints for 401 spikes and OTP failures

---

## Project structure

```
eco_chain/
├── eco_chain/              # Project config (settings, urls, wsgi, asgi)
├── apps/
│   ├── authentication/     # Signup, OTP verify, login, JWT refresh
│   ├── plants/             # Plant catalogue, UserPlant, CareTask
│   │   └── management/commands/seed_plants.py
│   ├── impact/             # ImpactLog (water saved, CO₂ offset)
│   ├── dashboard/          # Aggregated home-screen endpoint
│   └── green_match/        # Plant recommendation engine
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── manage.py
```