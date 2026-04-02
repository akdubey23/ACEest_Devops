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

### Git tags (phase milestones)

Annotated tags mark each major phase commit (`git tag -l -n1`). **`v1.0.0`** marks the submission snapshot with README evidence placeholders, CI, and tests. The **phase-\*** tags point at older commits—check out any tag to inspect that phase’s tree.

| Tag | Approx. source / theme |
|-----|-------------------------|
| `phase-1-v1.0` | Baseline program catalog (v1.0) |
| `phase-2-v1.1.2` | In-memory clients, CSV export |
| `phase-3-tests` | Pytest scaffolding + requirements (pre–SQLite) |
| `phase-4-v2.0.1` | SQLite persistence for clients |
| `phase-5-stabilization` | Phase 5 stabilization / metadata |
| `phase-6-v2.2.1` | Progress / adherence chart |
| `phase-7-v2.2.4` | Workouts + body metrics |
| `phase-8-auth-ai-pdf` | Auth, AI program, PDF report |
| `phase-9-membership` | Membership refactor |
| `phase-10-v3.2.4` | Phase 10 cleanup (v3.2.4 baseline) |
| `v1.0.0` | Submission snapshot: README + screenshot placeholders + GitHub Actions + Jenkins + full test suite |

## CI/CD integration

- **GitHub Actions** (`.github/workflows/main.yml`) runs on push and pull request: install deps, `compileall`, pytest with JUnit/HTML/Allure outputs, artifact upload, Docker build.
- **Jenkins** (`Jenkinsfile`) runs checkout, dependency install, tests (including Windows-friendly Python discovery), and Docker build on your agent.

## Screenshots (evidence)

Put PNG files in **`assets/screenshots/`** using these **exact names** (same as your image files, including spaces and underscores):

| Save as this filename |
|----------------------|
| `Jenkins pipeline stages.png` |
| `Jenkin_Test.png` |
| `GitHub Actions workflow.png` |
| `Docker image build.png` |
| `Docker container run.png` |
| `Health check.png` |

### Jenkins

![Jenkins pipeline stages](assets/screenshots/Jenkins%20pipeline%20stages.png)

![Jenkin_Test](assets/screenshots/Jenkin_Test.png)

### GitHub Actions

![GitHub Actions workflow](assets/screenshots/GitHub%20Actions%20workflow.png)

### Docker

![Docker image build](assets/screenshots/Docker%20image%20build.png)

![Docker container run](assets/screenshots/Docker%20container%20run.png)

### API

![Health check](assets/screenshots/Health%20check.png)

## License / course use

This repository is intended for academic DevOps assignments (version control, CI/CD, containers). Adjust licensing and deployment notes for your institution’s requirements.
