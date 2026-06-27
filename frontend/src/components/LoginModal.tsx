import { useState } from "react"
import { api } from "../api/client"

interface LoginModalProps {
  onLogin: () => void
}

export function LoginModal({ onLogin }: LoginModalProps) {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [open, setOpen] = useState(false)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const res = await api.auth.login({ username, password })
      localStorage.setItem("admin_token", res.access_token)
      setOpen(false)
      onLogin()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed")
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem("admin_token")
    onLogin()
  }

  const token = localStorage.getItem("admin_token")

  return (
    <>
      <button className="login-btn" onClick={() => (token ? handleLogout() : setOpen(true))}>
        {token ? "Logout" : "Admin Login"}
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
              <button type="button" onClick={() => setOpen(false)} className="cancel-btn">
                Cancel
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  )
}
