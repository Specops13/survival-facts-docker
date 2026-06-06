# Survival Facts

A self-contained survival reference wiki served by nginx in a Docker container.

## Features

- Eight detailed survival reference sections with search, bookmarks, and offline downloads
- Emergency Quick Actions for lost, injured, cold/wet, and safe-water scenarios
- Persistent 10-item kit checklist with packing progress
- Shareable section links, dark/light themes, collapsible sections, and mobile navigation
- Multi-platform Docker image for `amd64` and `arm64`

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

## Test

```bash
python -m unittest discover -s tests -v
```

## What's inside

| File | Purpose |
|------|---------|
| `index.html` | Single-page survival wiki with interactive field-reference tools |
| `Dockerfile` | `nginx:alpine` base, static site copy, and healthcheck |
| `docker-compose.yml` | Registry image, port mapping, restart policy, and healthcheck |
| `tests/test_site.py` | Structural regression tests for the page and Docker configuration |
