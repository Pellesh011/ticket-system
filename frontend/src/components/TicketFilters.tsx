import { useEffect, useRef, useState } from "react"
import type { SortLevel, TicketFilters as Filters, TicketPriority, TicketStatus } from "../api/types"

interface TicketFiltersProps {
  filters: Filters
  onFilterChange: (partial: Partial<Filters>) => void
}

function SortRow({
  level,
  index,
  onChange,
  onRemove,
}: {
  level: SortLevel
  index: number
  onChange: (index: number, level: SortLevel) => void
  onRemove: (index: number) => void
}) {
  return (
    <div className="sort-row">
      <select
        value={level.field}
        onChange={(e) => onChange(index, { ...level, field: e.target.value as SortLevel["field"] })}
      >
        <option value="created_at">Created At</option>
        <option value="priority">Priority</option>
      </select>
      <select
        value={level.order}
        onChange={(e) => onChange(index, { ...level, order: e.target.value as SortLevel["order"] })}
      >
        <option value="desc">Desc</option>
        <option value="asc">Asc</option>
      </select>
      {index > 0 && (
        <button type="button" className="remove-sort" onClick={() => onRemove(index)}>
          ✕
        </button>
      )}
    </div>
  )
}

export function TicketFilters({ filters, onFilterChange }: TicketFiltersProps) {
  const [search, setSearch] = useState(filters.search)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)

  useEffect(() => {
    return () => clearTimeout(debounceRef.current)
  }, [])

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setSearch(value)
    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      onFilterChange({ search: value })
    }, 300)
  }

  const handleSortChange = (index: number, level: SortLevel) => {
    const sort = [...filters.sort]
    sort[index] = level
    onFilterChange({ sort })
  }

  const handleSortRemove = (index: number) => {
    const sort = filters.sort.filter((_, i) => i !== index)
    onFilterChange({ sort })
  }

  const handleAddSort = () => {
    const usedFields = new Set(filters.sort.map((s) => s.field))
    const nextField = usedFields.has("created_at") ? "priority" : "created_at"
    onFilterChange({ sort: [...filters.sort, { field: nextField, order: "asc" }] })
  }

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
      <div className="sort-group">
        {filters.sort.map((level, i) => (
          <SortRow
            key={i}
            level={level}
            index={i}
            onChange={handleSortChange}
            onRemove={handleSortRemove}
          />
        ))}
        {filters.sort.length < 2 && (
          <button type="button" className="add-sort" onClick={handleAddSort}>
            + Add sort level
          </button>
        )}
      </div>
    </div>
  )
}
