# Survival Facts

A minimal static webpage that displays randomized survival facts, served via nginx in a Docker container.

## Quick start

```bash
docker compose up -d
```

Then open http://localhost:8080 in your browser.

## Build manually

```bash
docker build -t survival-facts .
docker run -d -p 8080:80 --name survival-facts survival-facts
```

## Stop

```bash
docker compose down
```

## What's inside

| File | Purpose |
|------|---------|
| `index.html` | Single-page app — 30 survival facts across 8 categories, randomized on load |
| `Dockerfile` | `nginx:alpine` base, copies static files, adds healthcheck |
| `docker-compose.yml` | Port mapping (8080→80), restart policy, healthcheck |
