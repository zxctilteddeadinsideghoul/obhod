# Obhod Frontend

React + Vite кабинет руководителя для системы обходов оборудования.

## Запуск

```bash
npm install
npm run dev
```

Vite поднимает dev-сервер на `http://localhost:5173`.

## Источник данных

Источник данных задается через `.env`.

Пример:

```bash
cp .env.example .env
```

Доступные режимы:

- `VITE_DATA_SOURCE=mock` — использовать локальные моковые данные;
- `VITE_DATA_SOURCE=backend` — использовать реальный backend.

Если выбран режим `backend`, укажи адрес Traefik HTTP entrypoint:

```env
VITE_API_BASE_URL=http://144.31.181.154
VITE_PROXY_TARGET=http://144.31.181.154
```

`Traefik` dashboard обычно доступен на `:8080`, но API приложения должен идти через HTTP entrypoint, в вашем текущем окружении это `http://144.31.181.154`.

## Реализованная логика

- `GET /api/auth/me`
- `GET /api/field/tasks/my`
- `GET /api/field/tasks/{round_id}`
- `POST /api/field/tasks/{round_id}/start`
- `GET /api/field/equipment`
- `GET /api/field/equipment/{equipment_id}`
- `GET /api/field/routes`
- `GET /api/field/routes/{route_id}`
