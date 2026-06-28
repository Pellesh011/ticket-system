import { useEffect, useRef, useState } from "react";
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { setFilters, selectFilters } from "./ticketsSlice";
import type { TicketFilters as Filters, TicketPriority, TicketStatus } from "../../api/types";

export function TicketFilters() {
  const dispatch = useAppDispatch();
  const filters = useAppSelector(selectFilters);

  const [search, setSearch] = useState(filters.search);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  useEffect(() => {
    return () => clearTimeout(debounceRef.current);
  }, []);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearch(value);
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      dispatch(setFilters({ search: value }));
    }, 300);
  };

  return (
    <div className="ticket-filters">
      <input
        type="text"
        placeholder="Поиск по названию или описанию..."
        value={search}
        onChange={handleSearchChange}
        className="search-input"
      />
      <select
        value={filters.status}
        onChange={(e) =>
          dispatch(setFilters({ status: e.target.value as TicketStatus | "" }))
        }
      >
        <option value="">Все статусы</option>
        <option value="new">Новый</option>
        <option value="in_progress">В работе</option>
        <option value="done">Выполнено</option>
      </select>
      <select
        value={filters.priority}
        onChange={(e) =>
          dispatch(setFilters({ priority: e.target.value as TicketPriority | "" }))
        }
      >
        <option value="">Все приоритеты</option>
        <option value="low">Низкий</option>
        <option value="normal">Средний</option>
        <option value="high">Высокий</option>
      </select>
      <select
        value={`${filters.sort_by}-${filters.sort_order}`}
        onChange={(e) => {
          const [sort_by, sort_order] = e.target.value.split("-") as [
            Filters["sort_by"],
            Filters["sort_order"],
          ];
          dispatch(setFilters({ sort_by, sort_order }));
        }}
      >
        <option value="created_at-desc">Сначала новые</option>
        <option value="created_at-asc">Сначала старые</option>
        <option value="priority-desc">Высокий приоритет</option>
        <option value="priority-asc">Низкий приоритет</option>
      </select>
      <select
        value={filters.page_size}
        onChange={(e) =>
          dispatch(setFilters({ page_size: Number(e.target.value), page: 1 }))
        }
      >
        <option value={5}>5 записей</option>
        <option value={10}>10 записей</option>
        <option value={20}>20 записей</option>
        <option value={50}>50 записей</option>
        <option value={100}>100 записей</option>
      </select>
    </div>
  );
}
