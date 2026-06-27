export type TicketStatus = "new" | "in_progress" | "done"

export type TicketPriority = "low" | "normal" | "high"

export interface Ticket {
  id: number
  title: string
  description: string | null
  status: TicketStatus
  priority: TicketPriority
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
  priority: TicketPriority
}

export interface TicketUpdate {
  title?: string
  description?: string
  priority?: TicketPriority
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

export interface SortLevel {
  field: "created_at" | "priority"
  order: "asc" | "desc"
}

export interface TicketFilters {
  status: TicketStatus | ""
  priority: TicketPriority | ""
  search: string
  sort: SortLevel[]
  page: number
  page_size: number
}
