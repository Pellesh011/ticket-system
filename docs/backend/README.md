# Бэкенд

Асинхронный REST API на FastAPI с чистой архитектурой.

## Стек

- Python 3.12
- FastAPI — асинхронный фреймворк
- SQLAlchemy 2.0 (async) + aiosqlite — ORM и доступ к SQLite
- Pydantic v2 — валидация, DTO, конфигурация
- Alembic — управление миграциями
- python-jose — JWT-аутентификация
- SlowAPI — rate limiting

## Структура

```
app/
├── core/                   # Ядро домена (чистая бизнес-логика)
│   ├── domain/
│   │   ├── entities.py     # Доменные сущности (dataclass): Ticket, User, Priority
│   │   ├── enums.py        # TicketStatus (TicketPriority удалён — теперь таблица)
│   │   ├── exceptions.py   # Иерархия доменных исключений
│   │   └── schemas.py      # Pydantic DTO (request/response)
│   ├── repositories/       # Абстракции репозиториев (порты)
│   │   ├── base.py         # Generic BaseRepository[T]
│   │   ├── priority_repository.py  # IPriorityRepository
│   │   ├── ticket_repository.py
│   │   └── user_repository.py
│   └── services/           # Интерфейсы сервисов (порты)
│       ├── auth_service.py
│       └── ticket_service.py
├── infrastructure/         # Конкретные реализации
│   ├── database/
│   │   ├── base.py         # DeclarativeBase
│   │   ├── models.py       # SQLAlchemy ORM-модели (TicketModel, PriorityModel, UserModel)
│   │   ├── types.py        # TZDateTime — TypeDecorator для timezone-aware datetime
│   │   ├── seed.py         # Сид приоритетов (low/normal/high) при первом запуске
│   │   ├── engine.py       # AsyncEngine + фабрика сессий
│   │   └── session.py      # Генератор сессий
│   ├── repositories/       # SQL-реализации + mapping
│   │   ├── sql_priority_repository.py
│   │   ├── sql_ticket_repository.py
│   │   └── sql_user_repository.py
│   └── security/           # Хеширование паролей (PBKDF2)
├── services/               # Бизнес-логика
│   ├── auth_service.py     # JWT, логин, верификация
│   ├── ticket_service.py   # CRUD, валидация бизнес-правил
│   └── priority_service.py # CRUD приоритетов
└── api/                    # HTTP-слой
    ├── routes/             # Эндпоинты
    ├── schemas/            # Переэкспорт DTO
    └── dependencies.py     # DI-провайдеры (FastAPI Depends)
```

## Принцип зависимостей

```
api → services → core ← infrastructure
```

Domain-слой (`core`) не зависит ни от каких внешних библиотек.

## Паттерны проектирования

### Repository Pattern

Абстрактные интерфейсы репозиториев в `core/repositories`, SQL-реализации в `infrastructure/repositories`. Полная развязка бизнес-логики от механизма сохранности.

- `BaseRepository[T]` — generic с методами `get_by_id`, `create`, `update`, `delete`
- `ITicketRepository` — добавляет `get_filtered(...)` с фильтром по `priority_id`
- `IPriorityRepository` — добавляет `get_all()` и `get_by_name(...)`
- `IUserRepository` — добавляет `get_by_username(...)`
- Mapping Layer — функции `_to_entity()` / `_from_entity()` конвертируют ORM-модели ↔ доменные сущности

### Dependency Injection

FastAPI `Depends()` в `dependencies.py` собирает граф зависимостей на каждый запрос:

```
DB Session → Repository → Service → Route Handler
```

### Exception Hierarchy

```
TicketDomainError (base)
├── TicketNotFoundError          # ticket_id
├── TicketDoneError              # action
│   ├── TicketDoneCannotEditError
│   ├── TicketDoneCannotDeleteError
│   └── TicketDoneCannotChangeStatusError
├── AuthenticationError
└── UnauthorizedError
```

Глобальный `exception_handler` преобразует их в HTTP-ответы.

### Другие паттерны

- **DTO** — Pydantic-модели разделяют контракт API и доменную модель
- **Facade** — `api/schemas/` переэкспортирует DTO из `core/domain/schemas`
- **Factory** — DI-функции и `async_session_factory`
- **Strategy** — `sort_by`/`sort_order` динамически определяют сортировку
- **Seed** — `seed_priorities()` заполняет таблицу `priorities` при первом запуске (выполняется в `lifespan`)
- **TZDateTime** — кастомный `TypeDecorator` хранит UTC naive datetime в SQLite, возвращает timezone-aware UTC при чтении
