export type TicketStatus = "new" | "in_progress" | "done"

export interface Priority {
  id: number
  name: string
  sort_order: number
}

export interface Ticket {
  id: number
  title: string
  description: string | null
  status: TicketStatus
  priority_id: number
  priority_name: string
  created_at: string
  updated_at: string
}

export interface PaginatedResponse {
  items: Ticket[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface TicketCreate {
  title: string
  description?: string
  priority_id: number
}

export interface TicketUpdate {
  title?: string
  description?: string
  priority_id?: number
}

export interface TicketStatusUpdate {
  status: TicketStatus
}

export interface LoginRequest {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface TicketFilters {
  status: TicketStatus | ""
  priority_id: number | ""
  search: string
  sort_by: "created_at" | "priority"
  sort_order: "asc" | "desc"
  page: number
  page_size: number
}
