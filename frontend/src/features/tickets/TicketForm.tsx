import { useState } from "react";
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { createTicket, selectPriorities, selectTicketsLoading } from "./ticketsSlice";

export function TicketForm() {
  const dispatch = useAppDispatch();
  const loading = useAppSelector(selectTicketsLoading);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const priorities = useAppSelector(selectPriorities);

  const [priority_id, setPriorityId] = useState<number>(2);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  const validate = (): boolean => {
    const errors: Record<string, string> = {};
    const trimmedTitle = title.trim();
    if (trimmedTitle.length < 3) {
      errors.title = "Название должно содержать минимум 3 символа";
    }
    if (trimmedTitle.length > 120) {
      errors.title = "Название должно содержать максимум 120 символов";
    }
    if (description.trim().length > 1000) {
      errors.description = "Описание должно содержать максимум 1000 символов";
    }
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    const result = await dispatch(
      createTicket({
        title: title.trim(),
        description: description.trim() || undefined,
        priority_id,
      }),
    );

    if (createTicket.fulfilled.match(result)) {
      setTitle("");
      setDescription("");
      setPriorityId(2);
      setFieldErrors({});
    }
  };

  return (
    <form onSubmit={handleSubmit} className="ticket-form">
      <h3>Создать тикет</h3>
      <div className="form-row">
        <div className="field">
          <input
            type="text"
            placeholder="Название (3-120 символов)"
            value={title}
            onChange={(e) => {
              setTitle(e.target.value);
              setFieldErrors((prev) => ({ ...prev, title: "" }));
            }}
            maxLength={120}
            required
            disabled={loading}
            className={fieldErrors.title ? "input-error" : ""}
          />
          {fieldErrors.title && (
            <span className="field-error">{fieldErrors.title}</span>
          )}
        </div>
        <select
          value={priority_id}
          onChange={(e) => setPriorityId(Number(e.target.value))}
          disabled={loading}
        >
          {priorities.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
      </div>
      <div className="field">
        <textarea
          placeholder="Описание (необязательно, макс. 1000 символов)"
          value={description}
          onChange={(e) => {
            setDescription(e.target.value);
            setFieldErrors((prev) => ({ ...prev, description: "" }));
          }}
          maxLength={1000}
          rows={2}
          disabled={loading}
          className={fieldErrors.description ? "input-error" : ""}
        />
        {fieldErrors.description && (
          <span className="field-error">{fieldErrors.description}</span>
        )}
      </div>
      <button type="submit" disabled={loading}>
        {loading ? "Создание..." : "Создать"}
      </button>
    </form>
  );
}
