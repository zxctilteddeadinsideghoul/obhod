# Auth Service

`auth-service` отвечает за проверку токена пользователя и передачу данных пользователя в остальные сервисы через Traefik ForwardAuth.

## Назначение

- проверяет `Authorization: Bearer ...`;
- определяет пользователя и роль;
- возвращает `X-User-Id`, `X-User-Role`, `X-User-Name` для внутренних сервисов;
- отделяет авторизацию от бизнесовой логики `field-service` и `report-service`.

## Роли и вход

Поддерживаются две роли:

- `WORKER` - работник/обходчик;
- `ADMIN` - начальник/администратор.

Для мобильного приложения и веб-интерфейса используется логин:

```http
POST /api/auth/login
Content-Type: application/json
```

Работник:

```json
{
  "username": "worker",
  "password": "worker123"
}
```

Администратор:

```json
{
  "username": "admin",
  "password": "admin123"
}
```

Ответ:

```json
{
  "access_token": "obhod...",
  "token_type": "bearer",
  "expires_in": 43200,
  "user": {
    "id": "dev-worker",
    "role": "WORKER",
    "name": "Development Worker"
  }
}
```

Дальше клиент передает:

```http
Authorization: Bearer obhod...
```

Старые demo-токены оставлены для совместимости:

```text
dev-token        -> WORKER
dev-admin-token  -> ADMIN
```

## API

### Health

```http
GET /api/auth/health
```

Проверка доступности сервиса.

### Логин

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

Назначение:

- мобильное приложение получает токен работника;
- веб-интерфейс начальника получает токен администратора;
- остальные сервисы не знают пароль пользователя, они видят только проверенный `Authorization`.

### Создание работника администратором

```http
POST /api/auth/admin/workers
Authorization: Bearer <admin_access_token>
Content-Type: application/json

{
  "username": "ivanov",
  "password": "ivanov123",
  "full_name": "Иванов Иван Иванович",
  "employee_id": "worker-ivanov",
  "qualification_id": "OPERATOR-TU",
  "department_id": "DEPT-UGP"
}
```

Ответ:

```json
{
  "id": "worker-ivanov",
  "username": "ivanov",
  "role": "WORKER",
  "full_name": "Иванов Иван Иванович",
  "active_flag": true,
  "qualification_id": "OPERATOR-TU",
  "department_id": "DEPT-UGP"
}
```

После этого работник может войти в мобильное приложение через `/api/auth/login`.

При создании работника сервис также создает/обновляет запись в `field_employee`, чтобы начальник мог назначить этому работнику обход.

### Проверка доступа для Traefik

```http
GET /api/auth/verify
Authorization: Bearer <access_token>
```

Используется Traefik middleware `forwardAuth`.

Если токен валиден, сервис возвращает `200 OK` и заголовки:

```http
X-User-Id: dev-admin
X-User-Role: ADMIN
X-User-Name: Development Admin
```

Если токен невалиден, возвращает `401 Unauthorized`.

### Текущий пользователь

```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

Возвращает:

```json
{
  "id": "dev-worker",
  "role": "WORKER",
  "name": "Development Worker"
}
```

## Конфигурация

Переменные окружения:

```text
SERVICE_NAME=auth-service
DEV_AUTH_TOKEN=dev-token
DEV_ADMIN_TOKEN=dev-admin-token
AUTH_SECRET=change-me-in-production
ACCESS_TOKEN_TTL_SEC=43200
WORKER_LOGIN=worker
WORKER_PASSWORD=worker123
ADMIN_LOGIN=admin
ADMIN_PASSWORD=admin123
```

`DATABASE_URL` передается через compose, но в текущей реализации auth-service не хранит пользователей в БД. Для хакатона пользователи задаются через env-переменные, а клиент получает подписанный access token.

## Взаимодействие с Traefik

Защищенные роуты `field-service` и `report-service` проходят через middleware:

```text
client -> Traefik -> auth-service /api/auth/verify -> target service
```

После успешной проверки Traefik прокидывает в целевой сервис:

```text
X-User-Id
X-User-Role
X-User-Name
```

## Локальный запуск

```bash
docker compose up -d auth-service traefik
```

Проверка:

```bash
curl -s http://127.0.0.1/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

```bash
curl -s http://127.0.0.1/api/auth/me \
  -H "Authorization: Bearer <access_token>"
```

## Кодовая структура

```text
app/api/routes/auth.py        HTTP endpoints
app/repositories/tokens.py    demo-token storage
app/use_cases/verify_access.py
app/use_cases/get_current_user.py
app/use_cases/create_worker.py
app/containers/container.py   dependency wiring
```
