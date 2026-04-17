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
