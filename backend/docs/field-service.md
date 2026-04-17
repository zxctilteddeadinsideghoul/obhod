# Field Service

`field-service` - основной сервис мобильного обходчика и администрирования полевых данных.

## Назначение

Сервис отвечает за:

- оборудование;
- маршруты обходов;
- назначенные обходы;
- чек-листы;
- подтверждение точки обхода через QR/NFC;
- ввод показаний оборудования;
- фотофиксацию и вложения;
- дефекты и их критичность;
- demo seed для заполнения тестовой БД.

## Основные сценарии

### Работник выполняет обход

1. Работник получает список задач.
2. Открывает обход.
3. Нажимает старт.
4. Подходит к оборудованию.
5. Сканирует QR/NFC.
6. Система открывает форму, привязанную к оборудованию.
7. Работник заполняет чек-лист и показания.
8. При отклонении система создает дефект.
9. Работник завершает обход.

### Начальник настраивает данные

1. Создает оборудование.
2. Создает шаблон чек-листа.
3. Создает маршрут.
4. Назначает обход работнику.

## API

Все основные роуты находятся под:

```http
/api/field
```

### Health

```http
GET /api/field/health
```

Проверка доступности field-service.

### Demo seed

```http
POST /api/field/admin/seed-demo
Authorization: Bearer dev-admin-token
```

Заполняет БД демо-данными:

- сотрудники;
- оборудование;
- параметры оборудования;
- маршруты;
- чек-листы;
- обходы.

### Администрирование

```http
POST /api/field/admin/equipment
POST /api/field/admin/checklists/templates
POST /api/field/admin/routes
POST /api/field/admin/rounds
```

Доступно только роли `ADMIN`.

Подробнее: [admin-field-api.md](./admin-field-api.md).

### Задачи обходчика

```http
GET /api/field/tasks/my
GET /api/field/tasks/{round_id}
POST /api/field/tasks/{round_id}/start
POST /api/field/tasks/{round_id}/steps/{route_step_id}/confirm
POST /api/field/tasks/{round_id}/finish
```

Ключевой endpoint для QR/NFC:

```http
POST /api/field/tasks/{round_id}/steps/{route_step_id}/confirm
```

Пример:

```json
{
  "confirm_by": "nfc",
  "scanned_value": "E4:9E:F3:64",
  "payload_json": {
    "lat": 55.751244,
    "lon": 37.618423
  }
}
```

Если QR/NFC не соответствует оборудованию в маршруте, сервис не откроет форму и вернет ошибку.

### Чек-листы

```http
GET /api/field/checklists/templates
GET /api/field/checklists/templates/{template_id}
POST /api/field/checklists/{checklist_instance_id}/items/{item_template_id}/result
```

Результат чек-листа может быть:

```text
ok
warning
critical
```

При `warning` или `critical` сервис автоматически создает дефект.

### Показания оборудования

```http
GET /api/field/equipment
GET /api/field/equipment/{equipment_id}
POST /api/field/equipment/{equipment_id}/readings
```

Фактическое показание проверяется по справочнику параметров:

```text
field_equipment_parameter_def
field_equipment_parameter_reading
```

Если значение выходит за допустимые или критические границы, сервис возвращает статус и может создать дефект.

### Фото и вложения

```http
POST /api/field/attachments
GET /api/field/attachments
GET /api/field/attachments/{attachment_id}/download
```

Метаданные хранятся в Postgres, файл хранится в MinIO.

### Дефекты

```http
GET /api/field/defects
GET /api/field/defects/{defect_id}
PATCH /api/field/defects/{defect_id}/status
PATCH /api/field/defects/{defect_id}/severity
```

Подробнее: [defect-api.md](./defect-api.md).

## Данные

Основные таблицы:

```text
field_equipment
field_equipment_parameter_def
field_equipment_parameter_reading
field_route_template
field_route_step
field_round_instance
field_checklist_template
field_checklist_item_template
field_checklist_instance
field_checklist_item_result
field_route_step_visit
field_attachment
field_defect
field_journal_entry
field_audit_log
```

## Критичность дефектов

Логика расчета находится в:

```text
app/domain/severity.py
```

Алгоритм учитывает:

- тип отклонения;
- выход за допустимые и критические границы;
- коэффициент стабильности оборудования;
- возможность ручного переопределения начальником.

## Конфигурация

Переменные окружения:

```text
SERVICE_NAME=field-service
DATABASE_URL=postgresql://obhod:obhod@postgres:5432/obhod
MINIO_ENDPOINT=http://minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=obhod-media
KAFKA_BOOTSTRAP_SERVERS=redpanda:9092
```

## Миграции

Миграции не должны выполняться автоматически при старте приложения.

Для применения миграций используется отдельный compose-сервис:

```bash
docker compose --profile tools run --rm field-migrations
```

После этого можно запускать приложение:

```bash
docker compose up -d field-service
```

## Локальный запуск

```bash
docker compose up -d postgres minio redpanda
docker compose --profile tools run --rm field-migrations
docker compose up -d auth-service field-service traefik
```

Проверка:

```bash
curl -s http://127.0.0.1/api/field/health
```

Seed:

```bash
curl -s -X POST http://127.0.0.1/api/field/admin/seed-demo \
  -H "Authorization: Bearer dev-admin-token"
```

## Кодовая структура

```text
app/api/routes/field.py              HTTP endpoints
app/models/field.py                  SQLAlchemy models
app/schemas/field.py                 Pydantic schemas
app/repositories/                    database access
app/use_cases/                       business operations
app/domain/severity.py               defect severity algorithms
app/services/storage.py              MinIO storage adapter
alembic/versions/                    migrations
```
