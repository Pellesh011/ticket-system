# Конфигурация бэкенда

## Переменные окружения

| Переменная | По умолчанию | Описание |
|-----------|-------------|----------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/tickets.db` | Строка подключения к БД |
| `DEBUG` | `false` | Режим отладки |
| `SECRET_KEY` | (генерируется автоматически) | Секрет для JWT |
| `ALGORITHM` | `HS256` | Алгоритм JWT |
| `TOKEN_EXPIRE_HOURS` | `24` | Время жизни токена (часы) |
| `ADMIN_USERNAME` | `admin` | Логин администратора |
| `ADMIN_PASSWORD` | (пусто) | Пароль администратора |
| `LOG_LEVEL` | `DEBUG` | Уровень логирования |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | Разрешённые origins для CORS |

## Файл .env

Создайте `backend/.env` на основе `backend/.env.example`:

```bash
DATABASE_URL=sqlite+aiosqlite:///./data/tickets.db
DEBUG=true
SECRET_KEY=your-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-password-here
LOG_LEVEL=DEBUG
```

## Зависимости

```
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
sqlalchemy[asyncio]>=2.0.0
aiosqlite>=0.20.0
alembic>=1.13.0
python-jose[cryptography]>=3.3.0
slowapi>=0.1.10
```

## Тестирование

```
httpx>=0.27.0
pytest>=8.0.0
pytest-asyncio>=0.24.0
ruff>=0.15.0
```

## Миграции

```bash
# Создание новой миграции
cd backend && alembic revision --autogenerate -m "описание"

# Применение миграций
alembic upgrade head

# Откат на одну миграцию
alembic downgrade -1
```
