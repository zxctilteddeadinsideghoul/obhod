# Obhod Backend

Backend infrastructure for the "Mobile inspector" hackathon MVP.

## Services

- `auth-service` - authentication and Traefik `forwardAuth` verification.
- `field-service` - field workflow boundary: tasks, inspections, equipment, checklists, defects, media sync.
- `report-service` - report generation boundary.

## Infrastructure

- Traefik as the single HTTP entrypoint.
- PostgreSQL for service data.
- MinIO for media and generated reports.
- Redpanda for asynchronous service events through the Kafka API.

## Local Run

```bash
docker compose up --build
```

Endpoints through Traefik:

```text
GET http://localhost/api/auth/health
GET http://localhost/api/field/health
GET http://localhost/api/reports/health
```

Protected routes use Traefik `forwardAuth`. For the initial scaffold, pass:

```text
Authorization: Bearer dev-token
```

For admin-only scaffold endpoints, pass:

```text
Authorization: Bearer dev-admin-token
```

## Smoke Tests

With Docker Compose services running:

```bash
python3 scripts/smoke_test.py
```

The smoke test covers:

- auth and role forwarding through Traefik;
- demo seed;
- admin creation of equipment, checklist template, route and round;
- worker task flow: start, QR confirmation, checklist submission and finish;
- equipment reading submission;
- attachment upload to MinIO, listing and download;
- supervisor reports and analytics;
- basic RBAC checks.

Optional environment variables:

```text
SMOKE_BASE_URL=http://127.0.0.1
SMOKE_WORKER_TOKEN=dev-token
SMOKE_ADMIN_TOKEN=dev-admin-token
```

## Domain Unit Tests

Severity and stability calculators can be checked without Docker:

```bash
PYTHONPATH=services/field-service python3 services/field-service/tests/test_severity_calculators.py
```
