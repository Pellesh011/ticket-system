from datetime import datetime

from pydantic import BaseModel, Field

from app.core.domain.enums import TicketStatus


class PriorityCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=20)
    sort_order: int = 0


class PriorityUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=20)
    sort_order: int | None = None


class PriorityResponse(BaseModel):
    id: int
    name: str
    sort_order: int

    model_config = {"from_attributes": True}


class TicketCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=120)
    description: str | None = Field(None, max_length=1000)
    priority_id: int = 2


class TicketUpdate(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=120)
    description: str | None = Field(None, max_length=1000)
    priority_id: int | None = None


class TicketStatusUpdate(BaseModel):
    status: TicketStatus


class TicketResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: TicketStatus
    priority_id: int
    priority_name: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
