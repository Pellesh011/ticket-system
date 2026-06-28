import { createSlice, createAsyncThunk, type PayloadAction } from "@reduxjs/toolkit";
import { api } from "../../api/client";
import type {
  Priority,
  Ticket,
  TicketCreate,
  TicketFilters,
  TicketStatusUpdate,
} from "../../api/types";
import type { RootState } from "../../app/store";

interface PaginationInfo {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

interface TicketsState {
  items: Ticket[];
  pagination: PaginationInfo;
  filters: TicketFilters;
  priorities: Priority[];
  loading: boolean;
  error: string | null;
}

const defaultFilters: TicketFilters = {
  status: "",
  priority_id: "",
  search: "",
  sort_by: "created_at",
  sort_order: "desc",
  page: 1,
  page_size: 20,
};

const initialState: TicketsState = {
  items: [],
  pagination: {
    total: 0,
    page: 1,
    page_size: 20,
    total_pages: 0,
  },
  filters: { ...defaultFilters },
  priorities: [],
  loading: false,
  error: null,
};

export const fetchTickets = createAsyncThunk(
  "tickets/fetchTickets",
  async (filters: TicketFilters, { rejectWithValue }) => {
    try {
      return await api.tickets.list(filters);
    } catch (err) {
      return rejectWithValue(
        err instanceof Error ? err.message : "Failed to load tickets",
      );
    }
  },
);

export const createTicket = createAsyncThunk(
  "tickets/createTicket",
  async (data: TicketCreate, { getState, rejectWithValue }) => {
    try {
      await api.tickets.create(data);
      const state = getState() as RootState;
      return await api.tickets.list(state.tickets.filters);
    } catch (err) {
      return rejectWithValue(
        err instanceof Error ? err.message : "Failed to create ticket",
      );
    }
  },
);

export const updateTicketStatus = createAsyncThunk(
  "tickets/updateTicketStatus",
  async (
    { id, data }: { id: number; data: TicketStatusUpdate },
    { getState, rejectWithValue },
  ) => {
    try {
      await api.tickets.updateStatus(id, data);
      const state = getState() as RootState;
      return await api.tickets.list(state.tickets.filters);
    } catch (err) {
      return rejectWithValue(
        err instanceof Error ? err.message : "Failed to update status",
      );
    }
  },
);

export const deleteTicket = createAsyncThunk(
  "tickets/deleteTicket",
  async (id: number, { getState, rejectWithValue }) => {
    try {
      await api.tickets.delete(id);
      const state = getState() as RootState;
      return await api.tickets.list(state.tickets.filters);
    } catch (err) {
      return rejectWithValue(
        err instanceof Error ? err.message : "Failed to delete ticket",
      );
    }
  },
);

export const fetchPriorities = createAsyncThunk(
  "tickets/fetchPriorities",
  async (_, { rejectWithValue }) => {
    try {
      return await api.priorities.list();
    } catch (err) {
      return rejectWithValue(
        err instanceof Error ? err.message : "Failed to load priorities",
      );
    }
  },
);

const ticketsSlice = createSlice({
  name: "tickets",
  initialState,
  reducers: {
    setFilters(state, action: PayloadAction<Partial<TicketFilters>>) {
      state.filters = { ...state.filters, ...action.payload, page: action.payload.page ?? 1 };
    },
    setPage(state, action: PayloadAction<number>) {
      state.filters.page = action.payload;
    },
    clearError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    function handleFetchFulfilled(
      state: TicketsState,
      action: PayloadAction<{
        items: Ticket[];
        total: number;
        page: number;
        page_size: number;
        total_pages: number;
      }>,
    ) {
      state.loading = false;
      state.items = action.payload.items;
      state.pagination = {
        total: action.payload.total,
        page: action.payload.page,
        page_size: action.payload.page_size,
        total_pages: action.payload.total_pages,
      };
    }

    builder
      .addCase(fetchTickets.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchTickets.fulfilled, handleFetchFulfilled)
      .addCase(fetchTickets.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(fetchPriorities.fulfilled, (state, action) => {
        state.priorities = action.payload;
      })
      .addCase(createTicket.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createTicket.fulfilled, handleFetchFulfilled)
      .addCase(createTicket.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(updateTicketStatus.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateTicketStatus.fulfilled, handleFetchFulfilled)
      .addCase(updateTicketStatus.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(deleteTicket.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteTicket.fulfilled, handleFetchFulfilled)
      .addCase(deleteTicket.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { setFilters, setPage, clearError } = ticketsSlice.actions;

export const selectTickets = (state: RootState) => state.tickets.items;
export const selectPagination = (state: RootState) => state.tickets.pagination;
export const selectFilters = (state: RootState) => state.tickets.filters;
export const selectPriorities = (state: RootState) => state.tickets.priorities;
export const selectTicketsLoading = (state: RootState) => state.tickets.loading;
export const selectTicketsError = (state: RootState) => state.tickets.error;

export default ticketsSlice.reducer;
