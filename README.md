# Survival Facts

A fast, self-contained survival reference wiki served by nginx in a Docker container.

## Features

- Search-first interface with ranked topic-level results, synonyms, previews, and keyboard navigation
- Detailed water, fire, shelter, navigation, food, first aid, signaling, mindset, weather, and vehicle guidance
- Four offline SVG knot diagrams: figure-eight, bowline, taut-line hitch, and clove hitch
- Each knot uses a three-stage tying sequence, contrasting working end, and finished-knot checkpoints
- Survival-priority planner and water-planning estimator
- Emergency Quick Actions and a persistent 10-item kit checklist
- Shareable topic links, bookmarks, themes, offline downloads, and mobile navigation
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
| `index.html` | Search-first single-page survival wiki and interactive tools |
| `Dockerfile` | `nginx:alpine` base, static site copy, and healthcheck |
| `docker-compose.yml` | Registry image, port mapping, restart policy, and healthcheck |
| `tests/test_site.py` | Structural regression tests for the page and Docker configuration |

## Safety references

Content is educational and does not replace emergency services or certified training. Key official references include:

- [CDC Heat and Health](https://www.cdc.gov/heat-health/)
- [National Weather Service Lightning Safety](https://www.weather.gov/safety/lightning)
- [National Weather Service Flood Safety](https://www.weather.gov/safety/flood)
- [Ready.gov Car Safety](https://www.ready.gov/car)
- [OSHA Heat Illness Prevention](https://www.osha.gov/heat-exposure/water-rest-shade)
