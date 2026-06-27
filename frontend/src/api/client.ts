import type {
  LoginRequest,
  PaginatedResponse,
  Ticket,
  TicketCreate,
  TicketFilters,
  TicketStatusUpdate,
  TicketUpdate,
  TokenResponse,
} from "./types"

const API_BASE = import.meta.env.VITE_API_URL || ""

class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = "ApiError"
    this.status = status
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = sessionStorage.getItem("admin_token")
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  }
  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  })

  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: "Unknown error" }))
    throw new ApiError(response.status, body.detail || "Request failed")
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json()
}

export const api = {
  tickets: {
    list(filters: TicketFilters): Promise<PaginatedResponse> {
      const params = new URLSearchParams()
      if (filters.status) params.set("status", filters.status)
      if (filters.priority) params.set("priority", filters.priority)
      if (filters.search) params.set("search", filters.search)
      params.set("sort_by", filters.sort_by)
      params.set("sort_order", filters.sort_order)
      params.set("page", String(filters.page))
      params.set("page_size", String(filters.page_size))
      return request(`/api/tickets?${params}`)
    },

    get(id: number): Promise<Ticket> {
      return request(`/api/tickets/${id}`)
    },

    create(data: TicketCreate): Promise<Ticket> {
      return request("/api/tickets", {
        method: "POST",
        body: JSON.stringify(data),
      })
    },

    update(id: number, data: TicketUpdate): Promise<Ticket> {
      return request(`/api/tickets/${id}`, {
        method: "PATCH",
        body: JSON.stringify(data),
      })
    },

    updateStatus(id: number, data: TicketStatusUpdate): Promise<Ticket> {
      return request(`/api/tickets/${id}/status`, {
        method: "PATCH",
        body: JSON.stringify(data),
      })
    },

    delete(id: number): Promise<void> {
      return request(`/api/tickets/${id}`, {
        method: "DELETE",
      })
    },
  },

  auth: {
    login(data: LoginRequest): Promise<TokenResponse> {
      return request("/api/auth/login", {
        method: "POST",
        body: JSON.stringify(data),
      })
    },
  },
}
