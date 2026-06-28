class TicketDomainError(Exception):
    pass


class TicketNotFoundError(TicketDomainError):
    def __init__(self, ticket_id: int) -> None:
        self.ticket_id = ticket_id
        super().__init__(f"Тикет с id {ticket_id} не найден")


class TicketDoneError(TicketDomainError):
    def __init__(self, action: str) -> None:
        self.action = action
        super().__init__(f"Невозможно {action} тикет в статусе 'выполнено'")

    def __str__(self) -> str:
        return f"Невозможно {self.action} тикет в статусе 'выполнено'"


class TicketDoneCannotEditError(TicketDoneError):
    def __init__(self) -> None:
        super().__init__(action="edit")


class TicketDoneCannotDeleteError(TicketDoneError):
    def __init__(self) -> None:
        super().__init__(action="delete")


class TicketDoneCannotChangeStatusError(TicketDoneError):
    def __init__(self) -> None:
        super().__init__(action="change status of")


class TicketInvalidStatusTransitionError(TicketDomainError):
    def __init__(self, current: str, target: str) -> None:
        self.current = current
        self.target = target
        super().__init__(f"Невозможно перейти из '{current}' в '{target}'")


class AuthenticationError(TicketDomainError):
    def __init__(self) -> None:
        super().__init__("Неверные учётные данные")


class UnauthorizedError(TicketDomainError):
    def __init__(self) -> None:
        super().__init__("Требуется доступ администратора")
