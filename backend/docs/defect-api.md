# Defect Management API

API для начальника. Все ручки требуют роль `ADMIN`.

```http
Authorization: Bearer <admin_access_token>
```

## Список дефектов

```http
GET /api/field/defects
```

Query params:

- `status` - фильтр по статусу;
- `severity` - фильтр по тяжести;
- `equipment_id` - фильтр по оборудованию;
- `limit` - размер страницы, по умолчанию `50`;
- `offset` - смещение, по умолчанию `0`.

Пример:

```http
GET /api/field/defects?status=detected&severity=critical
```

## Карточка дефекта

```http
GET /api/field/defects/{defect_id}
```

Возвращает:

- оборудование;
- дату обнаружения;
- источник дефекта;
- рассчитанную тяжесть;
- статус;
- `payload_json.severity` с объяснением расчёта;
- `payload_json.stability` с коэффициентом стабильности оборудования.

## Изменить статус дефекта

```http
PATCH /api/field/defects/{defect_id}/status
Content-Type: application/json

{
  "status": "in_review",
  "comment": "Принято в разбор мастером смены"
}
```

Допустимые статусы:

```text
detected
in_review
accepted
in_work
resolved
closed
rejected
```

История изменений сохраняется в `payload_json.statusHistory`.

## Изменить тяжесть дефекта

```http
PATCH /api/field/defects/{defect_id}/severity
Content-Type: application/json

{
  "severity": "high",
  "comment": "Повышено из-за влияния на технологический процесс"
}
```

Допустимые значения:

```text
info
low
medium
high
critical
```

Ручные корректировки сохраняются в `payload_json.severityOverrides`.
