# Admin Field API

API для веб-интерфейса начальника. Все ручки требуют роль `ADMIN`.

```http
Authorization: Bearer <admin_access_token>
```

## Создать оборудование

```http
POST /api/field/admin/equipment
```

Минимальный body:

```json
{
  "id": "EQ-DEMO-9001",
  "name": "Демо вентилятор ВД-9001",
  "type_id": "fan",
  "location": "Демо участок",
  "tech_no": "VD9001"
}
```

Если `qr_tag` не передан, backend создаст его автоматически:

```text
QR:EQ-DEMO-9001
```

## Создать шаблон чек-листа

```http
POST /api/field/admin/checklists/templates
```

Минимальный body:

```json
{
  "id": "TPL-DEMO-FAN-01",
  "name": "Демо осмотр вентилятора",
  "equipment_type_id": "fan",
  "items": [
    {
      "seq_no": 1,
      "question": "Вентилятор работает без постороннего шума",
      "answer_type": "bool",
      "required_flag": true
    },
    {
      "seq_no": 2,
      "question": "Температура корпуса",
      "answer_type": "number",
      "required_flag": true,
      "norm_ref": "TEMP_CASE"
    }
  ]
}
```

## Создать маршрут

```http
POST /api/field/admin/routes
```

Минимальный body:

```json
{
  "id": "ROUTE-DEMO-FAN",
  "name": "Демо маршрут вентилятора",
  "duration_min": 30,
  "planning_rule": "manual",
  "steps": [
    {
      "seq_no": 1,
      "equipment_id": "EQ-DEMO-9001",
      "checkpoint_id": "CP-FAN",
      "mandatory_flag": true,
      "confirm_by": "qr"
    }
  ]
}
```

Если `id` шага не передан, backend создаст его автоматически:

```text
ROUTE-DEMO-FAN-STEP-1
```

## Назначить обход работнику

```http
POST /api/field/admin/rounds
```

Минимальный body:

```json
{
  "id": "ROUND-DEMO-FAN-001",
  "route_template_id": "ROUTE-DEMO-FAN",
  "checklist_template_id": "TPL-DEMO-FAN-01",
  "employee_id": "dev-worker",
  "planned_start": "2026-04-17T18:00:00Z"
}
```

Если `planned_end` не передан, backend посчитает его по `duration_min` маршрута.

После создания обход появится у работника:

```http
GET /api/field/tasks/my
Authorization: Bearer <access_token>
```

После сканирования QR оборудования backend вернёт чек-лист:

```http
POST /api/field/tasks/ROUND-DEMO-FAN-001/steps/ROUTE-DEMO-FAN-STEP-1/confirm
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "confirm_by": "qr",
  "scanned_value": "QR:EQ-DEMO-9001"
}
```
