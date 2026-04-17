# Report Service

`report-service` отвечает за отчеты и аналитику для начальника.

## Назначение

Сервис читает данные, накопленные `field-service`, и формирует:

- список отчетов по обходам;
- детальный отчет конкретного обхода;
- сводные показатели;
- аналитику по оборудованию;
- аналитику по работникам;
- экспорт отчетов в файлы.

`report-service` не создает обходы и не изменяет результаты обходов. Его основная роль - чтение, агрегация и выгрузка данных.

## Доступ

Отчеты доступны только роли `ADMIN`.

Работник с `Bearer dev-token` получает `403 Forbidden`.

Токен начальника:

```text
Authorization: Bearer dev-admin-token
```

## API

Все роуты находятся под:

```http
/api/reports
```

### Health

```http
GET /api/reports/health
```

Проверка доступности сервиса.

### Текущий пользователь

```http
GET /api/reports/whoami
```

Возвращает пользователя, которого передал Traefik после проверки в `auth-service`.

### Список отчетов по обходам

```http
GET /api/reports/rounds
```

Query params:

```text
status
employee_id
limit
offset
```

Назначение: таблица обходов для интерфейса начальника.

### Детальный отчет обхода

```http
GET /api/reports/rounds/{round_id}
```

Содержит:

- общую информацию по обходу;
- результаты чек-листа;
- показания оборудования;
- дефекты;
- вложения и фотофиксацию с `download_url`.

### Экспорт отчета обхода

```http
GET /api/reports/rounds/{round_id}/export?format=csv
GET /api/reports/rounds/{round_id}/export?format=json
GET /api/reports/rounds/{round_id}/export?format=pdf
```

Форматы:

- `csv` - табличная выгрузка;
- `json` - полный структурированный отчет;
- `pdf` - оформленный PDF-файл на русском языке с таблицами и сводными блоками.

### Сводка

```http
GET /api/reports/analytics/summary
```

Возвращает:

- общее количество обходов;
- количество обходов по статусам;
- количество открытых дефектов;
- количество warning/critical отклонений;
- средний процент выполнения.

### Аналитика по оборудованию

```http
GET /api/reports/analytics/equipment?limit=20
```

Показывает оборудование, которое чаще попадает в дефекты или отклонения.

### Аналитика по работникам

```http
GET /api/reports/analytics/employees?limit=20
```

Показывает:

- количество назначенных и завершенных обходов;
- количество подтвержденных точек;
- среднее время выполнения;
- найденные warning/critical отклонения.

### Экспорт аналитики

```http
GET /api/reports/analytics/export?format=csv&limit=20
GET /api/reports/analytics/export?format=json&limit=20
GET /api/reports/analytics/export?format=pdf&limit=20
```

Экспорт включает:

- summary;
- analytics/equipment;
- analytics/employees.

Подробнее: [report-api.md](./report-api.md).

## Данные

`report-service` читает таблицы `field-service`:

```text
field_round_instance
field_route_template
field_route_step
field_route_step_visit
field_employee
field_checklist_instance
field_checklist_item_template
field_checklist_item_result
field_equipment
field_equipment_parameter_def
field_equipment_parameter_reading
field_defect
field_attachment
```

Собственной доменной схемы БД у сервиса пока нет.

## Экспорт PDF

PDF формируется через `ReportLab` с DejaVu-шрифтом, поэтому поддерживает русский текст.

В PDF входят:

- русские заголовки и подписи;
- сводные карточки по обходу или аналитике;
- таблицы чек-листов, показаний, дефектов и вложений;
- простые визуальные индикаторы выполнения и риска.

## Конфигурация

Переменные окружения:

```text
SERVICE_NAME=report-service
DATABASE_URL=postgresql://obhod:obhod@postgres:5432/obhod
MINIO_ENDPOINT=http://minio:9000
KAFKA_BOOTSTRAP_SERVERS=redpanda:9092
```

`MINIO_ENDPOINT` сейчас нужен для общей конфигурации, но сами файлы скачиваются через `field-service` по `download_url`.

## Локальный запуск

```bash
docker compose up -d postgres minio redpanda auth-service field-service report-service traefik
```

Проверка:

```bash
curl -s http://127.0.0.1/api/reports/health \
  -H "Authorization: Bearer dev-admin-token"
```

Экспорт PDF:

```bash
curl -L "http://127.0.0.1/api/reports/rounds/ROUND-2026-04-17-000123/export?format=pdf" \
  -H "Authorization: Bearer dev-admin-token" \
  -o round-report.pdf
```

## Кодовая структура

```text
app/api/routes/reports.py             HTTP endpoints
app/repositories/reports.py           SQL queries and aggregations
app/schemas/report.py                 Pydantic schemas
app/reports/                          документы и рендереры CSV/JSON/PDF
app/services/report_export.py         совместимый импорт сервиса экспорта
app/use_cases/                        report use cases
app/containers/container.py           dependency wiring
```
