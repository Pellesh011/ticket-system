import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { api } from "../../api/client";
import type { RootState } from "../../app/store";

interface AuthState {
  token: string | null;
  isAdmin: boolean;
  loading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  token: sessionStorage.getItem("admin_token"),
  isAdmin: !!sessionStorage.getItem("admin_token"),
  loading: false,
  error: null,
};

export const loginAsync = createAsyncThunk(
  "auth/login",
  async (
    { username, password }: { username: string; password: string },
    { rejectWithValue },
  ) => {
    try {
      const res = await api.auth.login({ username, password });
      sessionStorage.setItem("admin_token", res.access_token);
      return res.access_token;
    } catch (err) {
      return rejectWithValue(
        err instanceof Error ? err.message : "Login failed",
      );
    }
  },
);

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    logout(state) {
      state.token = null;
      state.isAdmin = false;
      state.error = null;
      sessionStorage.removeItem("admin_token");
    },
    checkAuth(state) {
      const token = sessionStorage.getItem("admin_token");
      state.token = token;
      state.isAdmin = !!token;
    },
    clearError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loginAsync.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loginAsync.fulfilled, (state, action) => {
        state.loading = false;
        state.token = action.payload;
        state.isAdmin = true;
      })
      .addCase(loginAsync.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { logout, checkAuth, clearError } = authSlice.actions;

export const selectIsAdmin = (state: RootState) => state.auth.isAdmin;
export const selectAuthLoading = (state: RootState) => state.auth.loading;
export const selectAuthError = (state: RootState) => state.auth.error;
export const selectToken = (state: RootState) => state.auth.token;

export default authSlice.reducer;
