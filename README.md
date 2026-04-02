# ACEest Fitness API

A REST API for gym and client management: programs, clients, workouts, progress analytics, authentication, AI-style program suggestions, PDF reports, and membership tracking. Built for DevOps coursework and local or containerized deployment.

## Description

ACEest Fitness API replaces ad-hoc spreadsheets and desktop-only tools with a single HTTP service. Trainers and integrations can create and update client profiles, log workouts and body metrics, review adherence and weight trends, export data (CSV, PDF), and check membership status—without sharing one physical machine or database file path by hand.

## Features

| Area | Capabilities |
|------|----------------|
| **CRUD** | Program catalog; create, read, list, and patch clients; CSV export |
| **Analytics** | Gym-wide adherence chart data; per-client adherence history; weight-over-time series; BMI from height and weight |
| **Auth** | Role-based login against a SQLite `users` table (default admin user for development) |
| **AI** | Rule-based weekly workout plan generator from client program and experience level |
| **PDF** | Per-client PDF report (client details and membership fields) |
| **Membership** | `membership_status` and `membership_end`; dedicated membership status lookup |

Data is stored in **SQLite** (path configurable via environment variable).

## Tech stack

- **Flask** — HTTP API
- **SQLite** — persistence (`sqlite3` standard library)
- **fpdf2** — PDF generation
- **pytest** — automated tests

## Setup

### Prerequisites

- Python 3.10+ recommended  
- `pip` (or `python -m pip`)

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Run the server

From the project root:

```bash
python app.py
```

The app listens on **http://127.0.0.1:5000** by default (`host=0.0.0.0`, `port=5000`).

### Database location

- Default file: `aceest_fitness.db` in the working directory  
- Override: set `ACEEST_DB_PATH` to an absolute path before starting the app (useful for tests and multiple environments)

```bash
# Windows PowerShell example
$env:ACEEST_DB_PATH = "C:\data\aceest.db"
python app.py
```

## API endpoints summary

Discovery and health:

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Service metadata, phase, and endpoint list |
| GET | `/health` | Liveness check |

Programs:

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/programs` | List all programs |
| GET | `/programs/<name>` | Single program details |

Clients:

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/clients` | List clients |
| POST | `/clients` | Create client record |
| GET | `/clients/<name>` | Latest record for that name |
| PATCH | `/clients/<name>` | Partial update (latest row) |
| GET | `/clients/export.csv` | CSV export |
| GET | `/clients/<name>/report.pdf` | PDF report |

Analytics and body metrics:

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/analytics/adherence` | Labels/values for chart (all clients) |
| GET | `/analytics/adherence/<client_name>` | Weekly adherence series |
| GET | `/analytics/weight-trend?client_name=` | Weight series from metrics |
| GET | `/bmi?client_name=` | BMI and category |

Workouts and metrics:

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/workouts` | Log workout (optional nested exercises) |
| GET | `/workouts?client_name=` | List workouts |
| POST | `/metrics` | Log weight / waist / bodyfat |

Auth, AI, membership:

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/auth/login` | JSON `username` / `password` |
| POST | `/ai/program` | JSON `client_name`, `experience` (`beginner` / `intermediate` / `advanced`) |
| GET | `/membership/status?client_name=` | Membership status and end date |

Errors return JSON: `{"error": "<message>"}` with appropriate HTTP status codes.

## Testing

Install dev/runtime dependencies (includes `pytest`):

```bash
python -m pip install -r requirements.txt
```

Run the full automated suite:

```bash
python -m pytest tests/ -v
```

The project includes an end-to-end test (`tests/test_final_e2e.py`) that exercises the main routes against a temporary database (`ACEEST_DB_PATH` set per test).

## Branching strategy

Aligned with a typical assignment Git flow (see also [BITS WILP-style example](https://github.com/2024tm93684/aceest-devops-assignment-01)):

| Branch | Role |
|--------|------|
| `master` | Stable integration; production-style baseline for submission |
| `develop` | Day-to-day integration; merge via PR when ready |
| `feature/*` | Optional short-lived branches for individual changes |

Flow: `feature/*` → `develop` → `master` (release). Release tags (e.g. `v1.0.0`) are cut from `master` when you freeze a submission snapshot.

## CI/CD integration

- **GitHub Actions** (`.github/workflows/main.yml`) runs on push and pull request: install deps, `compileall`, pytest with JUnit/HTML/Allure outputs, artifact upload, Docker build.
- **Jenkins** (`Jenkinsfile`) runs checkout, dependency install, tests (including Windows-friendly Python discovery), and Docker build on your agent.

## Screenshots (evidence)

Replace the placeholder images under `assets/screenshots/` with your own PNG or SVG exports (keep the same paths, or update the links below). Structure mirrors common DevOps assignment submissions.

### Jenkins pipeline

![Jenkins pipeline stages](assets/screenshots/placeholder-jenkins-stages.svg)

![Jenkins build console output](assets/screenshots/placeholder-jenkins-console.svg)

![Jenkins test result / artifacts](assets/screenshots/placeholder-jenkins-test-result.svg)

### GitHub Actions

![GitHub Actions workflow run](assets/screenshots/placeholder-github-actions.svg)

### Docker

![Docker image build](assets/screenshots/placeholder-docker-build.svg)

![Docker container run](assets/screenshots/placeholder-docker-run.svg)

### Tests and API

![Local or CI pytest run](assets/screenshots/placeholder-pytest-local.svg)

![Health check (browser or API client)](assets/screenshots/placeholder-health-check.svg)

## License / course use

This repository is intended for academic DevOps assignments (version control, CI/CD, containers). Adjust licensing and deployment notes for your institution’s requirements.
