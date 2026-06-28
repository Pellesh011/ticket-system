# Ticket Management System

Система управления заявками (тикетами) с REST API на бэкенде и SPA на фронтенде.

## Стек

| Слой | Технологии |
|------|-----------|
| Бэкенд | Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, JWT |
| Фронтенд | React 19, TypeScript 6, Redux Toolkit, Vite 8, Oxlint |
| Инфра | Docker Compose, Nginx, SQLite |

## Быстрый запуск

```bash
docker-compose up --build
```

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000/api`

## Тесты

```bash
# Backend (33 теста)
cd backend && pytest -v

# Frontend
cd frontend && npm run lint && npm run build
```

## Документация

| Раздел | Описание |
|--------|----------|
| [Бэкенд](docs/backend/README.md) | Архитектура, слои, паттерны, DI |
| [API](docs/backend/api.md) | Эндпоинты, запросы/ответы, ошибки |
| [Конфигурация](docs/backend/configuration.md) | Переменные окружения, .env, миграции |
| [Фронтенд](docs/frontend/README.md) | Архитектура, Redux, фичи, типизация |
| [Компоненты](docs/frontend/components.md) | Описание всех компонентов |
| [Деплой](docs/deployment.md) | Docker Compose, Nginx, продакшн |
| [Разработка](docs/development.md) | Локальная разработка, CI/CD, добавление фич |
