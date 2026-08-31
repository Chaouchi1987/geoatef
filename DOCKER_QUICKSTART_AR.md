# GeoAnomaly Pro — Docker Quick Start

## 1. Requirements
Install Docker Desktop (Windows/macOS) or Docker Engine + Compose (Linux).

## 2. Configure
Copy `.env.docker.example` to `.env`.

For local developer testing, keep `ALLOW_LOCAL_EE_AUTH=true` and authenticate
Earth Engine on the host if the local mode is used.

For production, configure Google OAuth and set a production redirect URI.

## 3. Start
```bash
docker compose up --build -d
```

## 4. Open
http://localhost:8080

API:
http://localhost:8000/docs

## 5. Stop
```bash
docker compose down
```

The Docker image contains the Python/FastAPI scientific backend and its
dependencies. The frontend is served by Nginx. User credentials are not baked
into the image.
