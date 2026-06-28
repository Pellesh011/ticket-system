# Разработка

Локальная разработка, тесты, CI/CD.

## Локальная разработка

### Backend

```bash
cd backend

# Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Копирование .env
cp .env.example .env

# Запуск сервера
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend

# Установка зависимостей
npm install

# Dev-сервер (порт 5173, прокси /api → localhost:8000)
npm run dev
```

## Тесты

### Backend

```bash
cd backend

# Все тесты (33: unit + integration)
pytest -v

# Только unit-тесты
pytest tests/unit/ -v

# Только integration-тесты
pytest tests/integration/ -v

# С覆盖率
pytest --cov=app --cov-report=term-missing
```

### Frontend

```bash
cd frontend

# Линтер
npm run lint

# Production-сборка
npm run build

# Предпросмотр production-сборки
npm run preview
```

## Миграции

```bash
cd backend

# Создание миграции
alembic revision --autogenerate -m "описание изменений"

# Применение всех миграций
alembic upgrade head

# Откат на одну миграцию
alembic downgrade -1

# Просмотр текущей версии
alembic current

# История миграций
alembic history
```

## CI/CD

GitHub Actions автоматически запускается при push/PR на `master`/`main`:

### backend-test
- Python 3.12
- `pytest -v` (33 теста)

### frontend-build
- Node 22
- `npm run lint` + `npm run build`

Джобы выполняются параллельно.

Результаты: https://github.com/Pellesh011/ticket-system/actions

## Структура PR

Рекомендуемый формат коммитов:

```
feat(scope): описание
fix(scope): описание
refactor(scope): описание
docs(scope): описание
```

Scopes: `backend`, `frontend`, `docs`, `ci`, `docker`

## Добавление нового эндпоинта

1. Определить DTO в `app/core/domain/schemas.py`
2. Добавить метод в репозиторий (`app/core/repositories/`)
3. Реализовать SQL-метод в `app/infrastructure/repositories/`
4. Добавить бизнес-логику в сервис (`app/services/`)
5. Создать эндпоинт в `app/api/routes/`
6. Добавить DI-провайдер в `app/api/dependencies.py` (если нужен новый сервис)
7. Написать тесты в `tests/`

## Добавление нового фича на фронтенде

1. Создать slice в `src/features/<feature>/`
2. Добавить async thunks для API-вызовов
3. Создать компоненты в `src/features/<feature>/`
4. Использовать `useAppSelector` / `useAppDispatch`
5. Подключить в `App.tsx`
