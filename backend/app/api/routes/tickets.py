import logging
from math import ceil
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_ticket_service, require_admin
from app.api.schemas.error import ErrorResponse
from app.api.schemas.pagination import PaginatedResponse
from app.api.schemas.ticket import (
    TicketCreate,
    TicketResponse,
    TicketStatusUpdate,
    TicketUpdate,
)
from app.core.domain.enums import TicketPriority, TicketStatus
from app.core.domain.exceptions import (
    TicketDoneCannotChangeStatusError,
    TicketDoneCannotDeleteError,
    TicketDoneCannotEditError,
    TicketNotFoundError,
)
from app.services.ticket_service import TicketService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/tickets", tags=["tickets"])


def _build_pagination(
    items: list[TicketResponse],
    total: int,
    page: int,
    page_size: int,
) -> PaginatedResponse:
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, ceil(total / page_size)),
    )


@router.post("", response_model=TicketResponse, status_code=201, responses={400: {"model": ErrorResponse}})
async def create_ticket(
    data: TicketCreate,
    service: Annotated[TicketService, Depends(get_ticket_service)],
) -> TicketResponse:
    return await service.create_ticket(data)


@router.get("", response_model=PaginatedResponse)
async def list_tickets(
    service: Annotated[TicketService, Depends(get_ticket_service)],
    status: TicketStatus | None = Query(None),
    priority: TicketPriority | None = Query(None),
    search: str | None = Query(None, min_length=1),
    sort_by: str = Query("created_at", pattern=r"^(created_at|priority)$"),
    sort_order: str = Query("desc", pattern=r"^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse:
    tickets, total = await service.get_tickets(
        status=status,
        priority=priority,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    return _build_pagination(tickets, total, page, page_size)


@router.get("/{ticket_id}", response_model=TicketResponse, responses={404: {"model": ErrorResponse}})
async def get_ticket(
    ticket_id: int,
    service: Annotated[TicketService, Depends(get_ticket_service)],
) -> TicketResponse:
    try:
        return await service.get_ticket(ticket_id)
    except TicketNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{ticket_id}", response_model=TicketResponse, responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}})
async def update_ticket(
    ticket_id: int,
    data: TicketUpdate,
    service: Annotated[TicketService, Depends(get_ticket_service)],
) -> TicketResponse:
    try:
        return await service.update_ticket(ticket_id, data)
    except TicketNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TicketDoneCannotEditError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{ticket_id}/status", response_model=TicketResponse, responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}})
async def update_ticket_status(
    ticket_id: int,
    data: TicketStatusUpdate,
    service: Annotated[TicketService, Depends(get_ticket_service)],
) -> TicketResponse:
    try:
        return await service.update_status(ticket_id, data)
    except TicketNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TicketDoneCannotChangeStatusError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{ticket_id}", status_code=204, responses={400: {"model": ErrorResponse}, 403: {"model": ErrorResponse}})
async def delete_ticket(
    ticket_id: int,
    service: Annotated[TicketService, Depends(get_ticket_service)],
    _: None = Depends(require_admin),
) -> None:
    try:
        await service.delete_ticket(ticket_id)
    except TicketNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TicketDoneCannotDeleteError as e:
        raise HTTPException(status_code=400, detail=str(e))
