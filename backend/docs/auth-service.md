# Auth Service

`auth-service` отвечает за проверку токена пользователя и передачу данных пользователя в остальные сервисы через Traefik ForwardAuth.

## Назначение

- проверяет `Authorization: Bearer ...`;
- определяет пользователя и роль;
- возвращает `X-User-Id`, `X-User-Role`, `X-User-Name` для внутренних сервисов;
- отделяет авторизацию от бизнесовой логики `field-service` и `report-service`.

## Роли

В текущем demo-режиме поддерживаются две роли:

- `WORKER` - работник/обходчик;
- `ADMIN` - начальник/администратор.

Demo-токены:

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

### Проверка доступа для Traefik

```http
GET /api/auth/verify
Authorization: Bearer dev-admin-token
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
Authorization: Bearer dev-token
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
```

`DATABASE_URL` передается через compose, но в текущей реализации auth-service не хранит пользователей в БД, а использует demo-token repository.

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
curl -s http://127.0.0.1/api/auth/me \
  -H "Authorization: Bearer dev-admin-token"
```

## Кодовая структура

```text
app/api/routes/auth.py        HTTP endpoints
app/repositories/tokens.py    demo-token storage
app/use_cases/verify_access.py
app/use_cases/get_current_user.py
app/containers/container.py   dependency wiring
```
