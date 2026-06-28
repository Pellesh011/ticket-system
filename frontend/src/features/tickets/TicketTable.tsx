import { memo } from "react";
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { selectIsAdmin } from "../auth/authSlice";
import {
  updateTicketStatus,
  deleteTicket,
  selectTickets,
} from "./ticketsSlice";
import type { Ticket, TicketStatus } from "../../api/types";

const statusColors: Record<TicketStatus, string> = {
  new: "status-new",
  in_progress: "status-progress",
  done: "status-done",
};

const statusLabels: Record<TicketStatus, string> = {
  new: "Новый",
  in_progress: "В работе",
  done: "Выполнено",
};

const priorityLabels: Record<string, string> = {
  low: "Низкий",
  normal: "Средний",
  high: "Высокий",
};

const validTransitions: Record<TicketStatus, TicketStatus[]> = {
  new: ["new", "in_progress"],
  in_progress: ["new", "in_progress", "done"],
  done: ["done"],
};

interface TicketRowProps {
  ticket: Ticket;
  isAdmin: boolean;
}

const TicketRow = memo(function TicketRow({ ticket, isAdmin }: TicketRowProps) {
  const dispatch = useAppDispatch();

  const handleStatusChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    dispatch(
      updateTicketStatus({
        id: ticket.id,
        data: { status: e.target.value as TicketStatus },
      }),
    );
  };

  const handleDelete = () => {
    if (confirm("Вы уверены, что хотите удалить этот тикет?")) {
      dispatch(deleteTicket(ticket.id));
    }
  };

  const isDone = ticket.status === "done";

  return (
    <tr>
      <td>{ticket.title}</td>
      <td className="desc-cell">{ticket.description || "-"}</td>
      <td>
        <select
          className={`status-select ${statusColors[ticket.status]}`}
          value={ticket.status}
          onChange={handleStatusChange}
          disabled={isDone}
        >
          {validTransitions[ticket.status].map((s) => (
            <option key={s} value={s}>
              {statusLabels[s]}
            </option>
          ))}
        </select>
      </td>
      <td>
        <span className={`priority-badge priority-${ticket.priority}`}>
          {priorityLabels[ticket.priority]}
        </span>
      </td>
      <td className="date-cell">
        {new Date(ticket.created_at).toLocaleDateString()}
      </td>
      <td className="actions-cell">
        {isAdmin && !isDone && (
          <button className="delete-btn" onClick={handleDelete} title="Удалить">
            X
          </button>
        )}
      </td>
    </tr>
  );
});

export function TicketTable() {
  const tickets = useAppSelector(selectTickets);
  const isAdmin = useAppSelector(selectIsAdmin);

  if (tickets.length === 0) {
    return <div className="empty-state">Тикеты не найдены</div>;
  }

  return (
    <div className="ticket-table-wrapper">
      <table className="ticket-table">
        <thead>
          <tr>
            <th>Название</th>
            <th>Описание</th>
            <th>Статус</th>
            <th>Приоритет</th>
            <th>Создан</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          {tickets.map((ticket) => (
            <TicketRow key={ticket.id} ticket={ticket} isAdmin={isAdmin} />
          ))}
        </tbody>
      </table>
    </div>
  );
}
