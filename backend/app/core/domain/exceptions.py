class TicketDomainError(Exception):
    pass


class TicketNotFoundError(TicketDomainError):
    def __init__(self, ticket_id: int) -> None:
        self.ticket_id = ticket_id
        super().__init__(f"Ticket with id {ticket_id} not found")


class TicketDoneError(TicketDomainError):
    def __init__(self, action: str) -> None:
        self.action = action
        super().__init__(f"Cannot {action} a ticket in 'done' status")

    def __str__(self) -> str:
        return f"Cannot {self.action} a ticket in 'done' status"


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
        super().__init__(f"Cannot transition from '{current}' to '{target}'")


class AuthenticationError(TicketDomainError):
    def __init__(self) -> None:
        super().__init__("Invalid credentials")


class UnauthorizedError(TicketDomainError):
    def __init__(self) -> None:
        super().__init__("Admin access required")
