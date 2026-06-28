import { useState } from "react";
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import {
  loginAsync,
  logout,
  clearError,
  selectIsAdmin,
  selectAuthLoading,
  selectAuthError,
} from "./authSlice";

export function LoginModal() {
  const dispatch = useAppDispatch();
  const isAdmin = useAppSelector(selectIsAdmin);
  const loading = useAppSelector(selectAuthLoading);
  const error = useAppSelector(selectAuthError);

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [open, setOpen] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await dispatch(loginAsync({ username, password }));
    if (loginAsync.fulfilled.match(result)) {
      setOpen(false);
      setUsername("");
      setPassword("");
    }
  };

  const handleLogout = () => {
    dispatch(logout());
  };

  const handleOpen = () => {
    dispatch(clearError());
    setOpen(true);
  };

  return (
    <>
      <button
        className="login-btn"
        onClick={() => (isAdmin ? handleLogout() : handleOpen())}
      >
        {isAdmin ? "Logout" : "Admin Login"}
      </button>
      {open && (
        <div className="modal-overlay" onClick={() => setOpen(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Admin Login</h3>
            {error && <div className="error-message">{error}</div>}
            <form onSubmit={handleLogin}>
              <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                disabled={loading}
              />
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
              />
              <button type="submit" disabled={loading}>
                {loading ? "Logging in..." : "Login"}
              </button>
              <button
                type="button"
                onClick={() => setOpen(false)}
                className="cancel-btn"
              >
                Cancel
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
