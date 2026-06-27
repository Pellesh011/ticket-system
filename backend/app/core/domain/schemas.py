from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field, PlainSerializer

from app.core.domain.enums import TicketPriority, TicketStatus


def _priority_from_any(v: object) -> TicketPriority | None:
    if v is None or isinstance(v, TicketPriority):
        return v
    if isinstance(v, str):
        return TicketPriority[v.upper()]
    if isinstance(v, int):
        return TicketPriority(v)
    raise ValueError(f"Invalid priority value: {v}")


PriorityField = Annotated[
    TicketPriority,
    BeforeValidator(_priority_from_any),
    PlainSerializer(lambda p: p.name.lower(), return_type=str),
]


class TicketCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=120)
    description: str | None = Field(None, max_length=1000)
    priority: PriorityField = TicketPriority.NORMAL


class TicketUpdate(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=120)
    description: str | None = Field(None, max_length=1000)
    priority: PriorityField | None = None


class TicketStatusUpdate(BaseModel):
    status: TicketStatus


class TicketResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: TicketStatus
    priority: PriorityField
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


