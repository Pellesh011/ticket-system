import { useState } from "react"
import type { TicketCreate, TicketPriority } from "../api/types"

interface TicketFormProps {
  onSubmit: (data: TicketCreate) => Promise<void>
}

export function TicketForm({ onSubmit }: TicketFormProps) {
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [priority, setPriority] = useState<TicketPriority>("normal")
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (title.trim().length < 3) {
      setError("Title must be at least 3 characters")
      return
    }
    setSubmitting(true)
    setError(null)
    try {
      await onSubmit({
        title: title.trim(),
        description: description.trim() || undefined,
        priority,
      })
      setTitle("")
      setDescription("")
      setPriority("normal")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create ticket")
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="ticket-form">
      <h3>Create Ticket</h3>
      {error && <div className="error-message">{error}</div>}
      <div className="form-row">
        <input
          type="text"
          placeholder="Title (3-120 chars)"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          maxLength={120}
          required
          disabled={submitting}
        />
        <select
          value={priority}
          onChange={(e) => setPriority(e.target.value as TicketPriority)}
          disabled={submitting}
        >
          <option value="low">Low</option>
          <option value="normal">Normal</option>
          <option value="high">High</option>
        </select>
      </div>
      <textarea
        placeholder="Description (optional, max 1000 chars)"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        maxLength={1000}
        rows={2}
        disabled={submitting}
      />
      <button type="submit" disabled={submitting}>
        {submitting ? "Creating..." : "Create"}
      </button>
    </form>
  )
}
