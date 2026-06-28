import { useEffect } from "react";
import { useAppDispatch, useAppSelector } from "./app/hooks";
import { fetchTickets, selectTicketsLoading, selectTicketsError, clearError } from "./features/tickets/ticketsSlice";
import { selectFilters } from "./features/tickets/ticketsSlice";
import { LoginModal } from "./features/auth/LoginModal";
import { TicketForm } from "./features/tickets/TicketForm";
import { TicketFilters } from "./features/tickets/TicketFilters";
import { TicketTable } from "./features/tickets/TicketTable";
import { Pagination } from "./features/tickets/Pagination";
import { ErrorMessage } from "./components/ErrorMessage";
import "./App.css";

function App() {
  const dispatch = useAppDispatch();
  const loading = useAppSelector(selectTicketsLoading);
  const error = useAppSelector(selectTicketsError);
  const filters = useAppSelector(selectFilters);

  useEffect(() => {
    dispatch(fetchTickets(filters));
  }, [dispatch, filters]);

  return (
    <div className="app">
      <header className="app-header">
        <h1>Ticket Management System</h1>
        <LoginModal />
      </header>

      <main className="app-main">
        <TicketForm />
        <TicketFilters />

        {error && (
          <ErrorMessage
            message={error}
            onDismiss={() => dispatch(clearError())}
          />
        )}

        {loading ? (
          <div className="loading-state">Loading tickets...</div>
        ) : (
          <TicketTable />
        )}

        <Pagination />
      </main>
    </div>
  );
}

export default App;
