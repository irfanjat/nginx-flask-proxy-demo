# Nginx Reverse Proxy + Flask API Demo

A practical demonstration of **Nginx as a reverse proxy** in front of a Flask REST API. The browser talks only to Nginx; Nginx forwards API requests to the backend and serves static files directly.

## Architecture

```
Client ──► localhost:8888 ──► Nginx (reverse proxy)
                                │
                                ├── /static/*  ──► served directly (fast, cached)
                                ├── /api/*     ──► proxy_pass ──► Flask (:5000)
                                ├── /health    ──► proxy_pass ──► Flask (:5000)
                                └── /          ──► serves index.html
```

## Features Demonstrated

- **Reverse proxy** — `proxy_pass` forwards requests to a backend upstream
- **Static file serving** — Nginx handles static assets with caching; Flask never sees them
- **Rate limiting** — 10 requests/second per IP with burst capacity
- **Proxy headers** — `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto` so Flask sees the real client
- **Upstream abstraction** — backend servers defined in an `upstream` block (ready for load balancing)
- **Timeouts & buffering** — production-grade proxy settings

## Quick Start

```bash
git clone <repo-url> nginx-flask-demo
cd nginx-flask-demo
docker compose up --build -d
```

Open **http://localhost:8888** — the frontend loads and talks to the API through Nginx.

### Verify it works

```bash
# Frontend
curl -s http://localhost:8888/ | head -3

# List notes (empty)
curl -s http://localhost:8888/api/notes

# Create a note
curl -s -X POST http://localhost:8888/api/notes \
  -H "Content-Type: application/json" \
  -d '{"title":"hello","content":"world"}'

# Health check
curl -s http://localhost:8888/health
```

## Project Structure

```
├── backend/
│   ├── app.py              # Flask CRUD API (notes)
│   ├── Dockerfile          # Container definition
│   └── requirements.txt
├── frontend/
│   └── index.html          # Vanilla JS frontend
├── nginx/
│   └── default.conf        # Nginx configuration
└── docker-compose.yml      # Orchestrates both services
```

## API Endpoints

All go through Nginx at `localhost:8888/api/notes`.

| Method | Path | Action |
|--------|------|--------|
| GET | `/api/notes` | List all notes |
| POST | `/api/notes` | Create a note |
| GET | `/api/notes/:id` | Get a note |
| PUT | `/api/notes/:id` | Update a note |
| DELETE | `/api/notes/:id` | Delete a note |
| GET | `/health` | Health check |

## Nginx Config Highlights (`nginx/default.conf`)

```nginx
# Upstream: where the backend lives
upstream flask_backend {
    server flask-app:5000;
    # Add more servers for load balancing:
    # server flask-app-2:5000 weight=2;
}

# Reverse proxy /api/* to Flask
location /api/ {
    limit_req zone=api_limit burst=20 nodelay;

    proxy_pass http://flask_backend;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    proxy_connect_timeout 60s;
    proxy_read_timeout    60s;
    proxy_send_timeout    60s;
}
```

## Running Without Docker

```bash
# 1. Install Flask deps
cd backend && pip install -r requirements.txt

# 2. Start Flask on port 5000
flask run --host=0.0.0.0 --port=5000 &

# 3. Update nginx/default.conf — change upstream to:
#    server 127.0.0.1:5000;

# 4. Start Nginx with the config
sudo nginx -c /absolute/path/to/nginx/default.conf
```

## License

MIT
