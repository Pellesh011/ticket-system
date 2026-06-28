interface ErrorMessageProps {
  message: string
  onDismiss?: () => void
}

export function ErrorMessage({ message, onDismiss }: ErrorMessageProps) {
  return (
    <div className="error-banner">
      <span>{message}</span>
      {onDismiss && <button onClick={onDismiss}>Закрыть</button>}
    </div>
  )
}
