import { useCallback, useState } from "react"
import "./App.css"
import type { TicketStatusUpdate } from "./api/types"
import { ErrorMessage } from "./components/ErrorMessage"
import { LoginModal } from "./components/LoginModal"
import { Pagination } from "./components/Pagination"
import { TicketFilters } from "./components/TicketFilters"
import { TicketForm } from "./components/TicketForm"
import { TicketTable } from "./components/TicketTable"
import { useTickets } from "./hooks/useTickets"

function App() {
  const {
    tickets,
    pagination,
    loading,
    error,
    filters,
    updateFilters,
    createTicket,
    updateStatus,
    deleteTicket,
    setPage,
  } = useTickets()

  const [isAdmin, setIsAdmin] = useState(!!localStorage.getItem("admin_token"))
  const [dismissedError, setDismissedError] = useState<string | null>(null)

  const handleLogin = useCallback(() => {
    setIsAdmin(!!localStorage.getItem("admin_token"))
  }, [])

  const handleStatusChange = useCallback(
    async (id: number, data: TicketStatusUpdate) => {
      await updateStatus(id, data)
    },
    [updateStatus],
  )

  const handleDelete = useCallback(
    async (id: number) => {
      if (confirm("Are you sure you want to delete this ticket?")) {
        await deleteTicket(id)
      }
    },
    [deleteTicket],
  )

  return (
    <div className="app">
      <header className="app-header">
        <h1>Ticket Management System</h1>
        <LoginModal onLogin={handleLogin} />
      </header>

      <main className="app-main">
        <TicketForm onSubmit={createTicket} />

        <TicketFilters filters={filters} onFilterChange={updateFilters} />

        {error && error !== dismissedError && (
          <ErrorMessage message={error} onDismiss={() => setDismissedError(error)} />
        )}

        {loading ? (
          <div className="loading-state">Loading tickets...</div>
        ) : (
          <TicketTable
            tickets={tickets}
            isAdmin={isAdmin}
            onStatusChange={handleStatusChange}
            onDelete={handleDelete}
          />
        )}

        <Pagination
          page={pagination.page}
          totalPages={pagination.total_pages}
          total={pagination.total}
          onPageChange={setPage}
        />
      </main>
    </div>
  )
}

export default App
