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
        placeholder="Search title or description..."
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
        <option value="">All Status</option>
        <option value="new">New</option>
        <option value="in_progress">In Progress</option>
        <option value="done">Done</option>
      </select>
      <select
        value={filters.priority}
        onChange={(e) =>
          dispatch(setFilters({ priority: e.target.value as TicketPriority | "" }))
        }
      >
        <option value="">All Priority</option>
        <option value="low">Low</option>
        <option value="normal">Normal</option>
        <option value="high">High</option>
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
        <option value="created_at-desc">Newest First</option>
        <option value="created_at-asc">Oldest First</option>
        <option value="priority-desc">Priority High</option>
        <option value="priority-asc">Priority Low</option>
      </select>
    </div>
  );
}
