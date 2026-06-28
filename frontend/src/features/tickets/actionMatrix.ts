import type { TicketStatus } from "../../api/types";

const ACTION_MATRIX: Record<string, Record<string, boolean>> = {
  new:         { edit: true, delete: true, transition: true },
  in_progress: { edit: true, delete: true, transition: true },
  done:        { edit: false, delete: false, transition: false },
};

const VALID_TRANSITIONS: Record<string, string[]> = {
  new:         ["new", "in_progress", "done"],
  in_progress: ["new", "in_progress", "done"],
  done:        ["done"],
};

export function canPerform(state: TicketStatus, action: string): boolean {
  return ACTION_MATRIX[state]?.[action] ?? false;
}

export function getAllowedTransitions(state: TicketStatus): TicketStatus[] {
  return (VALID_TRANSITIONS[state] ?? []) as TicketStatus[];
}
