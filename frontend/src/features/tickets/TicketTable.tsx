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

const priorityLabels: Record<string, string> = {
  low: "Low",
  normal: "Normal",
  high: "High",
};

interface TicketRowProps {
  ticket: Ticket;
  isAdmin: boolean;
}

const TicketRow = memo(function TicketRow({ ticket, isAdmin }: TicketRowProps) {
  const dispatch = useAppDispatch();

  const handleStatusChange = (status: TicketStatus) => {
    dispatch(updateTicketStatus({ id: ticket.id, data: { status } }));
  };

  const handleDelete = () => {
    if (confirm("Are you sure you want to delete this ticket?")) {
      dispatch(deleteTicket(ticket.id));
    }
  };

  return (
    <tr>
      <td>{ticket.title}</td>
      <td className="desc-cell">{ticket.description || "-"}</td>
      <td>
        <span className={`status-badge ${statusColors[ticket.status]}`}>
          {ticket.status.replace("_", " ")}
        </span>
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
        {ticket.status !== "done" ? (
          <select
            value={ticket.status}
            onChange={(e) => handleStatusChange(e.target.value as TicketStatus)}
          >
            <option value="new">New</option>
            <option value="in_progress">In Progress</option>
            <option value="done">Done</option>
          </select>
        ) : (
          <span className="done-label">Done</span>
        )}
        {isAdmin && ticket.status !== "done" && (
          <button className="delete-btn" onClick={handleDelete} title="Delete">
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
    return <div className="empty-state">No tickets found</div>;
  }

  return (
    <div className="ticket-table-wrapper">
      <table className="ticket-table">
        <thead>
          <tr>
            <th>Title</th>
            <th>Description</th>
            <th>Status</th>
            <th>Priority</th>
            <th>Created</th>
            <th>Actions</th>
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
