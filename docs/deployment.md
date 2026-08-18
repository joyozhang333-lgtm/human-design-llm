# Production Deployment

The production topology is a static React frontend behind Nginx plus a FastAPI service bound to localhost.

## Build

```bash
python -m pytest -q
cd web
npm ci
npm run build
```

## Backend

Install the Python package in a virtual environment, store runtime secrets outside the repository, and run:

```bash
uvicorn human_design.web_api:app --host 127.0.0.1 --port 8000
```

Use systemd or another process supervisor. The environment file should be readable only by the service account.

## Frontend And Nginx

Upload `web/dist/` to a versioned release directory and atomically switch a `current` symlink. Serve the SPA from that directory and proxy `/api/` to `http://127.0.0.1:8000`.

The HTML entry must not be cached across releases. Use `Cache-Control: no-cache, no-store, must-revalidate` for `/` and `/index.html`; hashed assets under `/assets/` may use long-lived immutable caching. This prevents an old public version badge and bundle from surviving a deployment.

Set the API proxy timeout to at least 180 seconds because model-backed readings can take longer than ordinary JSON requests.

## Verification

Verify all of the following after every release:

- `GET /api/health`
- `GET /api/product/providers` without exposing keys
- one anonymous `POST /api/charts`
- one main reading and one interpretation map
- one real chat request when a provider is configured
- desktop and mobile page rendering with no console errors

Never put server passwords, panel credentials, database passwords, or model API keys in this file or in deployment logs committed to Git.
