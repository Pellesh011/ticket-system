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
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})

  const validate = (): boolean => {
    const errors: Record<string, string> = {}
    const trimmedTitle = title.trim()
    if (trimmedTitle.length < 3) {
      errors.title = "Title must be at least 3 characters"
    }
    if (trimmedTitle.length > 120) {
      errors.title = "Title must be at most 120 characters"
    }
    if (description.trim().length > 1000) {
      errors.description = "Description must be at most 1000 characters"
    }
    setFieldErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return
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
      setFieldErrors({})
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
        <div className="field">
          <input
            type="text"
            placeholder="Title (3-120 chars)"
            value={title}
            onChange={(e) => { setTitle(e.target.value); setFieldErrors((prev) => ({ ...prev, title: "" })) }}
            maxLength={120}
            required
            disabled={submitting}
            className={fieldErrors.title ? "input-error" : ""}
          />
          {fieldErrors.title && <span className="field-error">{fieldErrors.title}</span>}
        </div>
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
      <div className="field">
        <textarea
          placeholder="Description (optional, max 1000 chars)"
          value={description}
          onChange={(e) => { setDescription(e.target.value); setFieldErrors((prev) => ({ ...prev, description: "" })) }}
          maxLength={1000}
          rows={2}
          disabled={submitting}
          className={fieldErrors.description ? "input-error" : ""}
        />
        {fieldErrors.description && <span className="field-error">{fieldErrors.description}</span>}
      </div>
      <button type="submit" disabled={submitting}>
        {submitting ? "Creating..." : "Create"}
      </button>
    </form>
  )
}
