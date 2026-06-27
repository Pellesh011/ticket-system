import { useCallback, useEffect, useState } from "react"
import { api } from "../api/client"
import type { Ticket, TicketCreate, TicketFilters, TicketStatusUpdate, TicketUpdate } from "../api/types"

interface PaginationInfo {
  total: number
  page: number
  page_size: number
  total_pages: number
}

export function useTickets() {
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [pagination, setPagination] = useState<PaginationInfo>({
    total: 0,
    page: 1,
    page_size: 20,
    total_pages: 0,
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState<TicketFilters>({
    status: "",
    priority: "",
    search: "",
    sort_by: "created_at",
    sort_order: "desc",
    page: 1,
    page_size: 20,
  })

  const fetchTickets = useCallback(async (f: TicketFilters) => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.tickets.list(f)
      setTickets(data.items)
      setPagination({
        total: data.total,
        page: data.page,
        page_size: data.page_size,
        total_pages: data.total_pages,
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load tickets")
      setTickets([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchTickets(filters)
  }, [filters, fetchTickets])

  const updateFilters = useCallback((partial: Partial<TicketFilters>) => {
    setFilters((prev) => ({
      ...prev,
      ...partial,
      page: partial.page ?? 1,
    }))
  }, [])

  const createTicket = useCallback(
    async (data: TicketCreate) => {
      setLoading(true)
      try {
        await api.tickets.create(data)
        await fetchTickets(filters)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to create ticket")
      } finally {
        setLoading(false)
      }
    },
    [filters, fetchTickets],
  )

  const updateStatus = useCallback(
    async (id: number, data: TicketStatusUpdate) => {
      setLoading(true)
      try {
        await api.tickets.updateStatus(id, data)
        await fetchTickets(filters)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to update status")
      } finally {
        setLoading(false)
      }
    },
    [filters, fetchTickets],
  )

  const updateTicket = useCallback(
    async (id: number, data: TicketUpdate) => {
      setLoading(true)
      try {
        await api.tickets.update(id, data)
        await fetchTickets(filters)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to update ticket")
      } finally {
        setLoading(false)
      }
    },
    [filters, fetchTickets],
  )

  const deleteTicket = useCallback(
    async (id: number) => {
      setLoading(true)
      try {
        await api.tickets.delete(id)
        await fetchTickets(filters)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to delete ticket")
      } finally {
        setLoading(false)
      }
    },
    [filters, fetchTickets],
  )

  const setPage = useCallback(
    (page: number) => {
      updateFilters({ page })
    },
    [updateFilters],
  )

  return {
    tickets,
    pagination,
    loading,
    error,
    filters,
    updateFilters,
    createTicket,
    updateStatus,
    updateTicket,
    deleteTicket,
    setPage,
    refresh: () => fetchTickets(filters),
  }
}
