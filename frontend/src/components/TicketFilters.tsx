import type { TicketFilters as Filters, TicketPriority, TicketStatus } from "../api/types"

interface TicketFiltersProps {
  filters: Filters
  onFilterChange: (partial: Partial<Filters>) => void
}

export function TicketFilters({ filters, onFilterChange }: TicketFiltersProps) {
  return (
    <div className="ticket-filters">
      <input
        type="text"
        placeholder="Search title or description..."
        value={filters.search}
        onChange={(e) => onFilterChange({ search: e.target.value })}
        className="search-input"
      />
      <select
        value={filters.status}
        onChange={(e) => onFilterChange({ status: e.target.value as TicketStatus | "" })}
      >
        <option value="">All Status</option>
        <option value="new">New</option>
        <option value="in_progress">In Progress</option>
        <option value="done">Done</option>
      </select>
      <select
        value={filters.priority}
        onChange={(e) => onFilterChange({ priority: e.target.value as TicketPriority | "" })}
      >
        <option value="">All Priority</option>
        <option value="low">Low</option>
        <option value="normal">Normal</option>
        <option value="high">High</option>
      </select>
      <select
        value={`${filters.sort_by}-${filters.sort_order}`}
        onChange={(e) => {
          const [sort_by, sort_order] = e.target.value.split("-") as [Filters["sort_by"], Filters["sort_order"]]
          onFilterChange({ sort_by, sort_order })
        }}
      >
        <option value="created_at-desc">Newest First</option>
        <option value="created_at-asc">Oldest First</option>
        <option value="priority-desc">Priority High</option>
        <option value="priority-asc">Priority Low</option>
      </select>
    </div>
  )
}
