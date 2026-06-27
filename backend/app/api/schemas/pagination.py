from app.core.domain.schemas import TicketResponse
from pydantic import BaseModel


class PaginatedResponse(BaseModel):
    items: list[TicketResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
