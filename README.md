# Transcriptions UI

A small web application for browsing interview metadata, streaming audio, and showing time-aligned transcripts. Backend in Python/Flask, frontend in Vue.js, deployed to Cloudflare Containers.

## Architecture

- **Backend**: Flask app serving the API, pre-signed media assets redirecting to cloud storage (`backend/`)
- **Storage**: Metadata stored locally in `backend/data/config.yml`, text and media assets stored in cloud buckets
- **Frontend**: Vue.js single-page application (`frontend/`), consuming the API
- **Infrastructure**: Docker image used locally and by Cloudflare Containers

## Prerequisites

- Python 3.12+
- Node.js 20+
- [uv](https://github.com/astral-sh/uv) for Python dependency management
- [Cloudflare Wrangler](https://developers.cloudflare.com/workers/wrangler/install-and-update/) for deploying to Cloudflare

## Configuration & Environment

The backend requires credentials for R2 and optional overrides for the config path and allowed origins.

Export the following environment variables: `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`.

## Local Development

### Backend

```bash
cd backend
uv sync
uv run flask --app app --debug run --port 8080
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Docker Workflow

Builds both frontend and backend into a single image served by Gunicorn.

```bash
docker build -t pn-transcriptions:latest .
docker run --rm \
  -p 8080:8080 \
  -e R2_ACCESS_KEY_ID=... \
  -e R2_SECRET_ACCESS_KEY=... \
  pn-transcriptions:latest
```

Set `CONFIG_PATH` or `ALLOWED_ORIGINS` via extra `-e` flags if you need overrides.

## Cloudflare Deployment

Deployment uses **Cloudflare Containers** managed via Wrangler:

1. `cd cloudflare`
2. Install dependencies: `npm install`
3. Authenticate: `npx wrangler login`
4. Configure secrets for R2: `npx wrangler secret put R2_ACCESS_KEY_ID`, `npx wrangler secret put R2_SECRET_ACCESS_KEY`
5. Deploy: `npm run deploy`

The worker proxy is implemented in `cloudflare/src/index.js`.

Run `npm run dev` to proxy through the Worker locally.

