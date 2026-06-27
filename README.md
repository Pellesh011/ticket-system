# Ticket Management System

Система управления заявками (тикетами) с REST API на бэкенде и SPA на фронтенде.

## Стек технологий

### Бэкенд
- **Python 3.12** / **FastAPI** — асинхронный REST API
- **SQLAlchemy 2.0** (async) + **aiosqlite** — ORM и доступ к SQLite
- **Pydantic v2** — валидация, DTO, конфигурация
- **Alembic** — управление миграциями (настроен)
- **python-jose** — JWT-аутентификация
- **pytest** + **pytest-asyncio** — тестирование

### Фронтенд
- **React 19** / **TypeScript 6** — SPA
- **Vite 8** — сборка и dev-сервер
- **Oxlint** — линтер

### Инфраструктура
- **Docker Compose** — оркестрация (backend на Uvicorn, frontend на Nginx)
- **Nginx** — раздача статики, проксирование `/api/` на бэкенд

## Архитектура бэкенда

```
app/
├── core/                   # Ядро домена (чистая бизнес-логика)
│   ├── domain/
│   │   ├── entities.py     # Доменные сущности (dataclass, без SQLAlchemy)
│   │   ├── models.py       # Re-export из entities (обратная совместимость)
│   │   ├── enums.py        # TicketStatus, TicketPriority
│   │   ├── exceptions.py   # Иерархия доменных исключений
│   │   └── schemas.py      # Pydantic DTO (request/response)
│   ├── repositories/       # Абстракции репозиториев (порты)
│   │   ├── base.py         # Generic BaseRepository[T]
│   │   ├── ticket_repository.py
│   │   └── user_repository.py
│   └── services/           # Интерфейсы сервисов (порты)
│       ├── auth_service.py
│       └── ticket_service.py
├── infrastructure/         # Конкретные реализации
│   ├── database/
│   │   ├── base.py         # DeclarativeBase
│   │   ├── models.py       # SQLAlchemy ORM-модели (TicketModel, UserModel)
│   │   ├── engine.py       # AsyncEngine + фабрика сессий
│   │   └── session.py      # Генератор сессий
│   ├── repositories/       # SQL-реализации + конвертация model ↔ entity
│   └── security/           # Хеширование паролей (PBKDF2)
├── services/               # Бизнес-логика (реализации сервисов)
│   ├── auth_service.py     # JWT, логин, верификация
│   └── ticket_service.py   # CRUD, валидация бизнес-правил
└── api/                    # HTTP-слой
    ├── routes/             # Эндпоинты (router)
    ├── schemas/            # Переэкспорт DTO для API
    └── dependencies.py     # DI-провайдеры (FastAPI Depends)
```

**Принцип зависимостей:** `api` → `services` → `core` ← `infrastructure`. Domain-слой (`core`) не зависит ни от каких внешних библиотек.

## Архитектура фронтенда

```
src/
├── api/
│   ├── client.ts           # Типизированный API-клиент (fetch)
│   └── types.ts            # TypeScript-интерфейсы (зеркало backend DTO)
├── hooks/
│   └── useTickets.ts       # Хук: состояние + запросы + CRUD
└── components/
    ├── App.tsx             # Корневой компонент-оркестратор
    ├── TicketForm.tsx      # Форма создания заявки
    ├── TicketFilters.tsx   # Поиск, фильтры, сортировка
    ├── TicketTable.tsx     # Таблица заявок
    ├── Pagination.tsx      # Навигация по страницам
    ├── LoginModal.tsx      # Модальное окно входа
    └── ErrorMessage.tsx    # Баннер ошибки
```

## Паттерны проектирования

### 1. Repository Pattern (Паттерн «Репозиторий»)

Самый выраженный паттерн в проекте. Абстрактные интерфейсы репозиториев (`BaseRepository[T]`, `ITicketRepository`, `IUserRepository`) расположены в слое `core/repositories`, а конкретные SQL-реализации — в `infrastructure/repositories`. Это полностью развязывает бизнес-логику от механизма сохранности.

- `BaseRepository[T]` — generic-абстракция с методами `get_by_id`, `create`, `update`, `delete`
- `ITicketRepository` — расширяет базовый, добавляя `get_filtered(...)`
- `IUserRepository` — расширяет базовый, добавляя `get_by_username(...)`
- В SQL-реализациях реализован **Mapping Layer** — функции `_to_entity()` / `_from_entity()` конвертируют SQLAlchemy модели в доменные сущности и обратно

### 2. Dependency Injection / Inversion of Control (Внедрение зависимостей / Инверсия управления)

FastAPI `Depends()` используется в `dependencies.py` для полной сборки графа зависимостей на каждый запрос:

```
DB Session → Repository → Service → Route Handler
```

Функции `get_ticket_service` и `get_auth_service` выступают фабриками, создавая репозиторий и инжектируя его в сервис. Маршруты объявляют зависимости через `Annotated[ServiceType, Depends(getter)]`.

### 3. Strategy Pattern (Паттерн «Стратегия»)

Параметры `sort_by` и `sort_order` в методе `get_filtered()` динамически определяют колонку и направление сортировки через `getattr(Ticket, sort_by)`, реализуя стратегию построения запроса.

### 4. DTO / Data Transfer Object (Паттерн «Объект передачи данных»)

Pydantic-модели разделяют контракт API и доменную модель:

- `TicketResponse` — ответ с `model_validate()` для конвертации из доменной сущности
- `TicketCreate`, `TicketUpdate`, `TicketStatusUpdate` — запросы с валидацией
- `PaginatedResponse[T]` — типизированный пагинированный ответ

### 5. Facade Pattern (Паттерн «Фасад»)

Модули `api/schemas/` (auth.py, ticket.py, pagination.py) — тонкие обёртки, переэкспортирующие DTO из `core/domain/schemas`. Предоставляют чистый путь импорта для API-слоя без прямой связанности с domain.

### 6. Factory Pattern (Паттерн «Фабрика»)

- Функции DI в `dependencies.py` выступают фабриками: собирают полный граф объектов (репозиторий + сервис)
- `async_session_factory` в `engine.py` — фабрика сессий БД

### 7. Exception Hierarchy / Error Object (Паттерн «Иерархия исключений»)

Структурированная иерархия доменных исключений:

```
TicketDomainError (base)
├── TicketNotFoundError          # carries ticket_id
├── TicketDoneError              # @dataclass, carries action
│   ├── TicketDoneCannotEditError
│   ├── TicketDoneCannotDeleteError
│   └── TicketDoneCannotChangeStatusError
├── AuthenticationError
└── UnauthorizedError
```

Глобальный `exception_handler` в FastAPI преобразует их в HTTP-ответы.

### 8. Custom Hook Pattern (Паттерн «Пользовательский хук» — React)

`useTickets` — хук, инкапсулирующий всё управление состоянием, запросы данных и CRUD-операции. Следует паттерну композиции: хук владеет состоянием, `App` распредляет данные и колбэки дочерним компонентам через props.

### 9. Middleware / Exception Handler (Паттерн «Middleware»)

Глобальный `@app.exception_handler(TicketDomainError)` преобразует доменные исключения в HTTP 400, работая на уровне middleware без создания пользовательских middleware-классов.

### 10. Generic Type Pattern (Паттерн «Дженерики»)

`BaseRepository[T]` использует Python `Generic[T]` для типобезопасного переиспользования абстракции репозитория разными сущностями (Ticket, User).

## API

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/auth/login` | Вход администратора (JWT) |
| `POST` | `/api/tickets` | Создание заявки |
| `GET` | `/api/tickets` | Список заявок (фильтры, сортировка, пагинация) |
| `GET` | `/api/tickets/{id}` | Получение заявки по ID |
| `PATCH` | `/api/tickets/{id}` | Обновление полей заявки |
| `PATCH` | `/api/tickets/{id}/status` | Изменение статуса заявки |
| `DELETE` | `/api/tickets/{id}` | Удаление заявки (только admin) |

## Бизнес-правила

- Заявка со статусом **done** не может быть отредактирована, удалена или иметь изменённый статус
- Название: 3–120 символов, описание: до 1000 символов
- Статус по умолчанию: `new`, приоритет: `normal`
- Единственный пользователь — admin, создаётся автоматически при первом входе

## Запуск

```bash
docker-compose up --build
```

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000/api`

## Тесты

```bash
# Backend (33 тестов: unit + integration)
cd backend && pytest -v

# Frontend (lint + build)
cd frontend && npm run lint && npm run build
```

## CI/CD

GitHub Actions автоматически запускается при push/PR на `master`/`main`:

- **backend-test** — Python 3.12, `pytest -v` (33 теста)
- **frontend-build** — Node 22, `npm run lint` + `npm run build`

Джобы выполняются параллельно. Результат: https://github.com/Pellesh011/ticket-system/actions

## Известные ограничения

- **Поиск по тексту:** поиск в тикетах (`GET /api/tickets?search=...`) использует `ILIKE %pattern%`, что вызывает full table scan. Для больших объёмов данных рекомендуется внедрить FTS5 (SQLite) или внешний поисковый движок.
