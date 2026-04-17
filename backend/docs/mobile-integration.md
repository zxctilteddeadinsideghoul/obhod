# Mobile API Integration

Документ описывает API, необходимые мобильному приложению обходчика на MIG-смартфоне.

## Base URL

При локальном запуске через Docker Compose:

```text
http://localhost
```

Все запросы мобильного приложения идут через Traefik API Gateway.

## Авторизация

Для защищённых endpoint'ов нужно передавать Bearer token:

```http
Authorization: Bearer dev-token
```

Тестовые токены:

```text
Работник:     Bearer dev-token
Начальник:    Bearer dev-admin-token
```

Gateway проверяет токен через `Auth Service` и прокидывает во внутренние сервисы доверенные заголовки:

```http
X-User-Id
X-User-Role
X-User-Name
```

Мобильное приложение эти заголовки вручную не отправляет.

## Основной сценарий мобильного обхода

1. Получить список назначенных обходов.
2. Открыть карточку нужного обхода.
3. Нажать "Старт обхода".
4. Подойти к оборудованию.
5. Отсканировать QR/NFC.
6. Получить форму проверки конкретного оборудования.
7. Заполнить пункты чек-листа.
8. Ввести показания оборудования.
9. Перейти к следующей точке.
10. Завершить обход.

---

## Auth Service

### Получить текущего пользователя

```http
GET /api/auth/me
```

Назначение: проверить, кто авторизован в мобильном приложении.

Headers:

```http
Authorization: Bearer dev-token
```

Response:

```json
{
  "id": "dev-worker",
  "role": "WORKER",
  "name": "Development Worker"
}
```

---

## Field Service

### Проверка доступности сервиса

```http
GET /api/field/health
```

Назначение: healthcheck для мобильного клиента.

Response:

```json
{
  "service": "field-service",
  "status": "ok"
}
```

---

### Получить назначенные обходы

```http
GET /api/field/tasks/my
```

Назначение: получить список обходов, назначенных текущему работнику.

Headers:

```http
Authorization: Bearer dev-token
```

Response:

```json
[
  {
    "id": "ROUND-2026-04-17-000123",
    "status": "planned",
    "route_id": "ROUTE-KC0103",
    "route_name": "КС0103",
    "planned_start": "2026-04-17T09:00:00Z",
    "planned_end": "2026-04-17T10:00:00Z",
    "completion_pct": 0
  }
]
```

Основные статусы:

```text
planned       обход запланирован
in_progress   обход выполняется
completed     обход завершён
```

---

### Получить карточку обхода

```http
GET /api/field/tasks/{round_id}
```

Назначение: получить маршрут, оборудование и связанную форму проверки.

Headers:

```http
Authorization: Bearer dev-token
```

Response:

```json
{
  "round": {
    "id": "ROUND-2026-04-17-000123",
    "status": "planned",
    "route_template_id": "ROUTE-KC0103",
    "employee_id": "dev-worker"
  },
  "route": {
    "id": "ROUTE-KC0103",
    "name": "КС0103",
    "steps": [
      {
        "id": "ROUTE-KC0103-STEP-1",
        "seq_no": 1,
        "equipment_id": "EQ-KC0103",
        "checkpoint_id": "PI-2",
        "mandatory_flag": true,
        "confirm_by": "nfc"
      }
    ]
  },
  "equipment": [
    {
      "id": "EQ-KC0103",
      "name": "Поршневая компрессорная установка КС-0103",
      "qr_tag": "QR:EQ-KC0103",
      "nfc_tag": "NFC:04AABB11CC"
    }
  ],
  "checklist_instance": {
    "id": "CL-2026-04-17-555",
    "status": "draft",
    "completion_pct": 0
  },
  "checklist_template": {
    "id": "TPL-EVERYDAY-SAFETY-02",
    "items": []
  }
}
```

Примечание: мобильное приложение не должно показывать полный чек-лист заранее как основной сценарий. Форма проверки открывается после успешного сканирования оборудования.

---

### Начать обход

```http
POST /api/field/tasks/{round_id}/start
```

Назначение: зафиксировать фактическое начало обхода.

Headers:

```http
Authorization: Bearer dev-token
```

Response:

```json
{
  "id": "ROUND-2026-04-17-000123",
  "status": "in_progress",
  "actual_start": "2026-04-17T09:10:00Z",
  "actual_end": null
}
```

---

### Подтвердить контрольную точку через QR/NFC

```http
POST /api/field/tasks/{round_id}/steps/{route_step_id}/confirm
```

Назначение: подтвердить, что работник физически подошёл к оборудованию. После успешного подтверждения backend возвращает форму проверки для этого оборудования.

Headers:

```http
Authorization: Bearer dev-token
Content-Type: application/json
```

Request:

```json
{
  "confirm_by": "qr",
  "scanned_value": "QR:EQ-KC0103",
  "payload_json": {
    "deviceId": "MIG-DEMO-001"
  }
}
```

Для NFC:

```json
{
  "confirm_by": "nfc",
  "scanned_value": "NFC:04AABB11CC"
}
```

Response:

```json
{
  "status": "confirmed",
  "visit": {
    "id": "15a5b295-4e0e-474b-a1d1-241887f29e73",
    "round_instance_id": "ROUND-2026-04-17-000123",
    "route_step_id": "ROUTE-KC0103-STEP-1",
    "equipment_id": "EQ-KC0103",
    "employee_id": "dev-worker",
    "confirmed_by": "qr",
    "scanned_value": "QR:EQ-KC0103",
    "confirmed_at": "2026-04-17T16:05:58Z",
    "status": "confirmed",
    "payload_json": {
      "deviceId": "MIG-DEMO-001"
    }
  },
  "equipment": {
    "id": "EQ-KC0103",
    "name": "Поршневая компрессорная установка КС-0103",
    "qr_tag": "QR:EQ-KC0103",
    "nfc_tag": "NFC:04AABB11CC"
  },
  "checklist_instance": {
    "id": "CL-2026-04-17-555",
    "status": "in_progress",
    "completion_pct": 0
  },
  "checklist_template": {
    "id": "TPL-EVERYDAY-SAFETY-02",
    "name": "Ежесменный осмотр компрессорной установки",
    "items": [
      {
        "id": "TPL-EVERYDAY-SAFETY-02-ITEM-1",
        "seq_no": 1,
        "question": "На оборудовании установлены защитные кожухи и блокировки",
        "answer_type": "bool",
        "required_flag": true
      }
    ]
  }
}
```

Ошибки:

```text
401 Unauthorized      нет токена или токен неверный
403 Forbidden         обход назначен другому работнику
404 Not Found         обход или точка маршрута не найдены
409 Conflict          QR/NFC не совпадает или обход уже завершён
```

---

### Отправить результат пункта формы

```http
POST /api/field/checklists/{checklist_instance_id}/items/{item_template_id}/result
```

Назначение: сохранить ответ работника по конкретному пункту формы проверки.

Headers:

```http
Authorization: Bearer dev-token
Content-Type: application/json
```

Request для boolean-поля:

```json
{
  "equipment_id": "EQ-KC0103",
  "result_code": "ok",
  "result_value": {
    "value": true
  },
  "comment": "Кожухи и блокировки на месте"
}
```

Request для числового поля:

```json
{
  "equipment_id": "EQ-KC0103",
  "result_code": "ok",
  "result_value": {
    "value": 1.5,
    "unit": "MPa"
  },
  "comment": "Давление в норме"
}
```

Response:

```json
{
  "result": {
    "id": "a7cdaab8-26df-4e85-bf55-f97d7a0333c7",
    "checklist_instance_id": "CL-2026-04-17-555",
    "item_template_id": "TPL-EVERYDAY-SAFETY-02-ITEM-1",
    "equipment_id": "EQ-KC0103",
    "result_code": "ok",
    "result_value": {
      "value": true
    },
    "comment": "Кожухи и блокировки на месте",
    "status": "normal"
  },
  "checklist_instance": {
    "id": "CL-2026-04-17-555",
    "status": "in_progress",
    "completion_pct": 50
  }
}
```

Статусы результата:

```text
normal     всё в порядке
warning    есть отклонение
critical   критическое отклонение
```

---

### Отправить показание оборудования

```http
POST /api/field/equipment/{equipment_id}/readings
```

Назначение: сохранить измеренное значение оборудования и автоматически проверить его по нормам.

Headers:

```http
Authorization: Bearer dev-token
Content-Type: application/json
```

Request:

```json
{
  "parameter_def_id": "PARAM-COMPRESSOR-PRESSURE-OUT",
  "value_num": 1.5,
  "source": "mobile",
  "route_step_id": "ROUTE-KC0103-STEP-1",
  "checklist_item_result_id": null,
  "payload_json": {
    "deviceId": "MIG-DEMO-001"
  }
}
```

Response при нормальном значении:

```json
{
  "reading": {
    "id": "24095ad7-d3f4-4777-822b-5f513c1c295d",
    "equipment_id": "EQ-KC0103",
    "parameter_def_id": "PARAM-COMPRESSOR-PRESSURE-OUT",
    "reading_ts": "2026-04-17T10:10:48Z",
    "value_num": 1.5,
    "value_text": null,
    "source": "mobile",
    "route_step_id": "ROUTE-KC0103-STEP-1",
    "checklist_item_result_id": null,
    "within_limits": true,
    "payload_json": {
      "status": "normal",
      "message": "Value is within configured limits"
    }
  },
  "status": "normal",
  "message": "Value is within configured limits"
}
```

Response при критическом отклонении:

```json
{
  "reading": {
    "equipment_id": "EQ-KC0103",
    "parameter_def_id": "PARAM-COMPRESSOR-PRESSURE-OUT",
    "value_num": 1.8,
    "within_limits": false
  },
  "status": "critical",
  "message": "Value is above critical maximum"
}
```

Статусы проверки:

```text
normal          значение в норме
warning         значение вне нормы
critical        критическое отклонение
not_evaluated   значение не удалось оценить
```

---

### Завершить обход

```http
POST /api/field/tasks/{round_id}/finish
```

Назначение: завершить обход и зафиксировать фактическое время окончания.

Headers:

```http
Authorization: Bearer dev-token
```

Response:

```json
{
  "id": "ROUND-2026-04-17-000123",
  "status": "completed",
  "actual_start": "2026-04-17T09:10:00Z",
  "actual_end": "2026-04-17T09:45:00Z"
}
```

Ошибки:

```text
409 Conflict   не заполнены обязательные пункты формы
403 Forbidden  обход назначен другому работнику
```

---

## Справочные endpoint'ы

### Список оборудования

```http
GET /api/field/equipment
```

Назначение: справочник оборудования. Для мобильного приложения может использоваться при предзагрузке данных.

---

### Карточка оборудования

```http
GET /api/field/equipment/{equipment_id}
```

Назначение: получить данные конкретного оборудования.

---

### Список маршрутов

```http
GET /api/field/routes
```

Назначение: справочник маршрутов. Обычно нужен для отладки или будущего офлайн-режима.

---

### Карточка маршрута

```http
GET /api/field/routes/{route_id}
```

Назначение: получить маршрут и его контрольные точки.

---

## Рекомендованный порядок вызовов

```text
GET  /api/auth/me
GET  /api/field/tasks/my
GET  /api/field/tasks/{round_id}
POST /api/field/tasks/{round_id}/start
POST /api/field/tasks/{round_id}/steps/{route_step_id}/confirm
POST /api/field/checklists/{checklist_instance_id}/items/{item_template_id}/result
POST /api/field/equipment/{equipment_id}/readings
POST /api/field/tasks/{round_id}/finish
```

## Что важно для мобильного приложения

- Полная форма проверки не должна считаться доступной до успешного QR/NFC-подтверждения точки.
- При сканировании нужно отправлять `confirm_by` и `scanned_value`.
- Если сервер вернул `409 Conflict`, форму открывать нельзя.
- Если нет связи, мобильное приложение в будущем должно сохранить действие локально через Room и синхронизировать позже.
- `completion_pct` можно использовать для отображения прогресса заполнения формы.
- `status = critical` по показанию нужно визуально выделять в интерфейсе.

## Тестовые demo-данные

Для локальной проверки можно использовать:

```text
round_id:              ROUND-2026-04-17-000123
route_step_id:         ROUTE-KC0103-STEP-1
equipment_id:          EQ-KC0103
checklist_instance_id: CL-2026-04-17-555
item_template_id 1:    TPL-EVERYDAY-SAFETY-02-ITEM-1
item_template_id 2:    TPL-EVERYDAY-SAFETY-02-ITEM-2
parameter_def_id:      PARAM-COMPRESSOR-PRESSURE-OUT
qr_tag:                QR:EQ-KC0103
nfc_tag:               NFC:04AABB11CC
```

Перед проверкой demo-данных можно вызвать:

```http
POST /api/field/admin/seed-demo
Authorization: Bearer dev-admin-token
```
