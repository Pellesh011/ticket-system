# Фронтенд

SPA на React с централизованным управлением состоянием через Redux Toolkit.

## Стек

- React 19 — UI-библиотека
- TypeScript 6 — типизация
- Redux Toolkit — управление состоянием
- react-redux — привязка Redux к React
- Vite 8 — сборка и dev-сервер
- Oxlint — линтер

## Структура

```
src/
├── app/
│   ├── store.ts              # Конфигурация Redux store
│   └── hooks.ts              # Типизированные хуки (useAppDispatch, useAppSelector)
├── features/
│   ├── auth/
│   │   ├── authSlice.ts      # Состояние авторизации + loginAsync
│   │   └── LoginModal.tsx    # Модальное окно входа
│   └── tickets/
│       ├── ticketsSlice.ts   # Состояние тикетов + CRUD thunks
│       ├── TicketForm.tsx    # Форма создания тикета
│       ├── TicketFilters.tsx # Фильтры, поиск, сортировка
│       ├── TicketTable.tsx   # Таблица тикетов
│       └── Pagination.tsx    # Пагинация
├── components/
│   └── ErrorMessage.tsx      # Баннер ошибки
├── api/
│   ├── client.ts             # HTTP-клиент с auth-интерцептором
│   └── types.ts              # TypeScript-интерфейсы (зеркало backend DTO)
├── App.tsx                   # Корневой компонент
└── main.tsx                  # Точка входа (Provider + store)
```

## Redux Store

### Структура

```typescript
{
  auth: {
    token: string | null,
    isAdmin: boolean,
    loading: boolean,
    error: string | null
  },
  tickets: {
    items: Ticket[],
    pagination: { total, page, page_size, total_pages },
    filters: TicketFilters,
    priorities: Priority[],
    loading: boolean,
    error: string | null
  }
}
```

### Auth Slice

| Экшен | Тип | Описание |
|-------|-----|----------|
| `loginAsync` | async thunk | Вход (username/password → token) |
| `logout` | sync | Выход (очищает sessionStorage) |
| `checkAuth` | sync | Проверка токена в sessionStorage |
| `clearError` | sync | Очистка ошибки |

### Tickets Slice

| Экшен | Тип | Описание |
|-------|-----|----------|
| `fetchTickets` | async thunk | Загрузка списка с фильтрами |
| `fetchPriorities` | async thunk | Загрузка списка приоритетов |
| `createTicket` | async thunk | Создание + рефетч списка |
| `updateTicketStatus` | async thunk | Смена статуса + рефетч |
| `deleteTicket` | async thunk | Удаление + рефетч |
| `setFilters` | sync | Обновление фильтров (сброс страницы) |
| `setPage` | sync | Переключение страницы |
| `clearError` | sync | Очистка ошибки |

## Типизация API

Все интерфейсы в `api/types.ts` зеркалят backend DTO:

```typescript
type TicketStatus = "new" | "in_progress" | "done"

interface Priority {
  id: number
  name: string
  sort_order: number
}

interface Ticket {
  id: number
  title: string
  description: string | null
  status: TicketStatus
  priority_id: number
  priority_name: string
  created_at: string
  updated_at: string
}

interface TicketFilters {
  status: TicketStatus | ""
  priority_id: number | ""
  search: string
  sort_by: "created_at" | "priority"
  sort_order: "asc" | "desc"
  page: number
  page_size: number
}
```

## Команды

```bash
cd frontend

npm run dev      # Dev-сервер (http://localhost:5173)
npm run build    # Production-сборка
npm run lint     # Линтер (oxlint)
npm run preview  # Предпросмотр production-сборки
```
