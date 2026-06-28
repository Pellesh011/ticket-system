# Деплой

Запуск через Docker Compose.

## Структура

```
docker-compose.yml
├── backend     → Python 3.12 + Uvicorn (порт 8000)
└── frontend    → Nginx (порт 80 → 5173)
```

## Запуск

```bash
docker-compose up --build
```

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000/api`

## Сервисы

### Backend

- **Образ:** `python:3.12-slim`
- **Сервер:** Uvicorn
- **БД:** SQLite (volume `tickets_data`)
- **Healthcheck:** `GET /api/health` каждые 30с

### Frontend

- **Сборка:** Node 20 (build stage) → Nginx (runtime)
- **Статика:** `dist/` → `/usr/share/nginx/html`
- **Проксирование:** `/api/` → backend:8000

## Nginx

Конфигурация в `frontend/nginx.conf`:

- Раздача статики (SPA с fallback на index.html)
- Проксирование `/api/` на backend
- Gzip-сжатие
- Кэширование статических ассетов

## Переменные окружения

Передаются через `docker-compose.yml` и `backend/.env`:

```yaml
environment:
  - ADMIN_USERNAME=admin
  - CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
```

## Volume

Данные SQLite хранятся в named volume `tickets_data` для сохранности между перезапусками.

## Продакшн-замечания

- **SQLite** подходит для малых/средних нагрузок. Для масштабирования — миграция на PostgreSQL.
- **SECRET_KEY** генерируется автоматически при каждом запуске (токены не переживают рестарт). В продакшене — задавать через переменную окружения.
- **CORS** — указать реальные домены в `CORS_ORIGINS`.
