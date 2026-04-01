# ShrinkURL - Scalable URL Shortener

A production-ready, full-stack URL shortening service built for horizontal scalability and high-throughput redirect performance.

## Architecture Overview

ShrinkURL uses a distributed architecture optimised for the read-heavy nature of URL shorteners (redirects happen ~100x more than URL creation):

- **Backend:** Django 6.0.3 + Django REST Framework with PostgreSQL
- **Frontend:** Next.js 16 + React 19 + Tailwind CSS
- **Caching:** Redis for sub-millisecond lookups
- **Distributed IDs:** Apache Zookeeper for collision-free ID allocation across multiple backend instances
- **Encoding:** Base62 for compact 7-character short codes supporting 3.5 trillion unique URLs

## Project Structure

```
shrinkURL/
├── backend/                 # Django API & redirector
│   ├── api/                 # URL shortening API
│   │   ├── models.py        # URLMapping model (BigAutoField)
│   │   ├── views.py         # URLMappingViewSet + shorten_url
│   │   ├── serializers.py   # URLShortenSerializer, URLMappingSerializer
│   │   ├── urls.py          # DRF router + API root
│   │   └── utils/
│   │       ├── base62.py    # Base62 encode/decode
│   │       └── range_manager.py  # Zookeeper ID range allocation
│   ├── redirector/          # High-performance redirect handler
│   │   └── views.py         # Redis-first redirect logic
│   ├── shrinkURL/           # Django settings
│   │   └── settings.py      # Database, Redis, DRF, logging config
│   ├── logs/                # Application logs (7 files by severity)
│   ├── staticfiles/         # Collected static files
│   ├── pyproject.toml       # UV dependencies
│   └── manage.py            # Django CLI
└── frontend/                # Next.js UI
    ├── components/
    │   ├── hero.tsx         # URL input form + API call
    │   ├── result-card.tsx  # Shortened URL display
    │   └── recent-activity.tsx  # URL history
    ├── app/                   # Next.js App Router
    ├── next.config.mjs        # API rewrite proxy
    └── package.json         # NPM dependencies
```

## Prerequisites

### Required Services

1. **PostgreSQL** (v14+)
2. **Redis** (v6+)
3. **Apache Zookeeper** (v3.8+) - or use fallback mode

### Quick Service Setup

```bash
# Docker (recommended)
docker run -d -p 5432:5432 -e POSTGRES_DB=ShrinkURL -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=secret postgres:16
docker run -d -p 6379:6379 redis:7
docker run -d -p 2181:2181 zookeeper:3.9
```

## Installation

### Backend Setup

```bash
cd backend

# Install dependencies with UV
uv sync

# Create environment file
cat > .env << EOF
SECRET_KEY=$(uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
ZOOKEEPER_HOSTS=localhost:2181
ZK_RANGE_SIZE=1000000
FRONTEND_URL=http://localhost:3000
EOF

# Run migrations
uv run python manage.py migrate

# Create admin user (optional, for browsable API)
uv run python manage.py createsuperuser

# Collect static files
uv run python manage.py collectstatic --noinput

# Start server
uv run python manage.py runserver
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

# Start dev server
npm run dev
```

## API Reference

### Browsable API

Visit `http://localhost:8000/api/` in your browser for the interactive DRF browsable API.

Log in at `http://localhost:8000/api-auth/login/` with your Django superuser credentials.

### Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/` | GET | No | API root - lists all endpoints |
| `/api/shorten/` | POST | No | Create short URL (used by frontend) |
| `/api/urls/` | GET/POST | No | List/create URL mappings |
| `/api/urls/{short_code}/` | GET/PUT/PATCH/DELETE | No | Retrieve/update/delete URL |
| `/api-auth/login/` | GET/POST | No | DRF login page |
| `/{short_code}` | GET | No | Redirect to original URL |

### Create Short URL

```bash
curl -X POST http://localhost:8000/api/shorten/ \
  -H "Content-Type: application/json" \
  -d '{"long_url": "https://example.com/very/long/url"}'
```

**Response:**

```json
{
  "id": 23000001,
  "long_url": "https://example.com/very/long/url",
  "short_code": "0Wg3wX9",
  "short_url": "http://localhost:8000/0Wg3wX9",
  "created_at": "2026-03-31T23:14:04.123456Z"
}
```

### Redirect

```bash
curl -I http://localhost:8000/0Wg3wX9
# HTTP/1.1 301 Moved Permanently
# Location: https://example.com/very/long/url
```

## Frontend Usage

1. Open `http://localhost:3000`
2. Enter a long URL in the input field
3. Click "Shorten"
4. Copy the generated short URL
5. Recently shortened URLs appear below the form

The frontend proxies `/api/*` requests to the backend during development.

## Environment Variables

### Backend (`.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | - | Django secret key |
| `DEBUG` | Yes | `false` | Debug mode |
| `ALLOWED_HOSTS` | Yes | - | Comma-separated hosts |
| `DB_NAME` | Yes | - | PostgreSQL database |
| `DB_USER` | Yes | - | PostgreSQL user |
| `DB_PASSWORD` | Yes | - | PostgreSQL password |
| `DB_HOST` | Yes | - | PostgreSQL host |
| `DB_PORT` | Yes | `5432` | PostgreSQL port |
| `REDIS_URL` | Yes | - | Redis connection URL |
| `ZOOKEEPER_HOSTS` | No | `localhost:2181` | Zookeeper ensemble |
| `ZK_RANGE_SIZE` | No | `1000000` | IDs per range allocation |
| `FRONTEND_URL` | Yes | - | CORS allowed origin |

### Frontend (`.env.local`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | - | Backend API base URL |

## Scaling Architecture

### Distributed ID Generation

Multiple Django instances can run simultaneously without ID collisions:

1. Each instance requests a 1M ID range from Zookeeper
2. Zookeeper atomically increments the counter with optimistic locking
3. Instances consume IDs locally from their range
4. When exhausted, they request a new range automatically

### Read Performance

Redirects use a cache-first strategy:

1. Check Redis (sub-millisecond)
2. Cache hit → immediate 301 redirect
3. Cache miss → query PostgreSQL
4. Store in Redis (24h TTL) for future requests

## Logging

Logs are written to both console and files in `backend/logs/`:

- `django.log` - All Django logs
- `debug.log` - Debug level
- `info.log` - Info level
- `warning.log` - Warning level
- `error.log` - Error level
- `critical.log` - Critical level

## Development Commands

```bash
# Backend
cd backend
uv run python manage.py runserver          # Start dev server
uv run python manage.py shell              # Django shell
uv run python manage.py dbshell            # PostgreSQL shell
uv run python manage.py createsuperuser    # Create admin

# Frontend
cd frontend
npm run dev                                 # Start dev server
npm run build                               # Production build
npm run start                               # Start production server
```

## Troubleshooting

### Zookeeper Connection Issues

If Zookeeper is unavailable, the app falls back to random ID ranges for local development. Check logs for:

```
WARNING: Using fallback range: X to Y
```

### Redis Connection Issues

Ensure Redis is running and `REDIS_URL` is correct. The app will fail on startup if Redis is required but unavailable.

### CORS Errors

Add your frontend URL to `CORS_ALLOWED_ORIGINS` in `backend/shrinkURL/settings.py` or set `FRONTEND_URL` in `.env`.

### Port Conflicts

- Backend: `8000`
- Frontend: `3000`
- PostgreSQL: `5432`
- Redis: `6379`
- Zookeeper: `2181`

## License

MIT License - See LICENSE file for details.
