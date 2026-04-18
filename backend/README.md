# Obhod Backend

Backend infrastructure for the "Mobile inspector" hackathon MVP.

## Quick Start

Основная инструкция для команды: [docs/quick-start.md](./docs/quick-start.md).

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

Protected routes use Traefik `forwardAuth`. First get a token:

```bash
curl -s http://127.0.0.1/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"worker","password":"worker123"}'
```

Then pass it to protected endpoints:

```text
Authorization: Bearer <access_token>
```

For admin-only endpoints, login as admin:

```bash
curl -s http://127.0.0.1/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

```text
Authorization: Bearer <admin_access_token>
```

Create a worker for the mobile app:

```bash
curl -s http://127.0.0.1/api/auth/admin/workers \
  -H "Authorization: Bearer <admin_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ivanov",
    "password": "ivanov123",
    "full_name": "Иванов Иван Иванович",
    "employee_id": "worker-ivanov",
    "qualification_id": "OPERATOR-TU",
    "department_id": "DEPT-UGP"
  }'
```

Then the worker logs in with `ivanov / ivanov123`.

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
- defect management: list, detail, status update and severity override;
- supervisor reports and analytics;
- basic RBAC checks.

Optional environment variables:

```text
SMOKE_BASE_URL=http://127.0.0.1
SMOKE_WORKER_TOKEN=<access_token>
SMOKE_ADMIN_TOKEN=<admin_access_token>
```

If tokens are not passed, smoke test logs in as `worker` and `admin` automatically.

## Domain Unit Tests

Severity and stability calculators can be checked without Docker:

```bash
PYTHONPATH=services/field-service python3 services/field-service/tests/test_severity_calculators.py
```
