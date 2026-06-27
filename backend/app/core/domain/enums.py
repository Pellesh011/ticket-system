from enum import IntEnum, StrEnum


class TicketStatus(StrEnum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TicketPriority(IntEnum):
    LOW = 0
    NORMAL = 1
    HIGH = 2

    @classmethod
    def _missing_(cls, value: object) -> "TicketPriority":
        if isinstance(value, str):
            try:
                return cls[value.upper()]
            except KeyError:
                pass
        return super()._missing_(value)
