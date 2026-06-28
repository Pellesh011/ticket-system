import logging
from math import ceil
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import (
    get_priority_service,
    get_ticket_service,
    require_admin,
)
from app.api.schemas.error import ErrorResponse
from app.api.schemas.ticket import (
    PriorityCreate,
    PriorityResponse,
    PriorityUpdate,
    TicketCreate,
    TicketResponse,
    TicketStatusUpdate,
    TicketUpdate,
)
from app.core.domain.enums import TicketStatus
from app.core.domain.exceptions import (
    TicketDoneCannotChangeStatusError,
    TicketDoneCannotDeleteError,
    TicketDoneCannotEditError,
    TicketInvalidStatusTransitionError,
    TicketNotFoundError,
)
from app.services.ticket_service import TicketService
from app.services.priority_service import PriorityService

from app.api.schemas.pagination import PaginatedResponse

logger = logging.getLogger(__name__)

ticket_router = APIRouter(prefix="/api/tickets", tags=["tickets"])
priority_router = APIRouter(prefix="/api/priorities", tags=["priorities"])


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


# --- Ticket routes ---


@ticket_router.post("", response_model=TicketResponse, status_code=201, responses={400: {"model": ErrorResponse}})
async def create_ticket(
    data: TicketCreate,
    service: Annotated[TicketService, Depends(get_ticket_service)],
) -> TicketResponse:
    return await service.create_ticket(data)


@ticket_router.get("", response_model=PaginatedResponse)
async def list_tickets(
    service: Annotated[TicketService, Depends(get_ticket_service)],
    status: TicketStatus | None = Query(None),
    priority_id: int | None = Query(None),
    search: str | None = Query(None, min_length=1),
    sort_by: str = Query("created_at", pattern=r"^(created_at|priority)$"),
    sort_order: str = Query("desc", pattern=r"^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse:
    tickets, total = await service.get_tickets(
        status=status,
        priority_id=priority_id,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    return _build_pagination(tickets, total, page, page_size)


@ticket_router.get("/{ticket_id}", response_model=TicketResponse, responses={404: {"model": ErrorResponse}})
async def get_ticket(
    ticket_id: int,
    service: Annotated[TicketService, Depends(get_ticket_service)],
) -> TicketResponse:
    try:
        return await service.get_ticket(ticket_id)
    except TicketNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@ticket_router.patch("/{ticket_id}", response_model=TicketResponse, responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}})
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


@ticket_router.patch("/{ticket_id}/status", response_model=TicketResponse, responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}})
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
    except TicketInvalidStatusTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))


@ticket_router.delete("/{ticket_id}", status_code=204, responses={400: {"model": ErrorResponse}, 403: {"model": ErrorResponse}})
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


# --- Priority routes ---


@priority_router.get("", response_model=list[PriorityResponse])
async def list_priorities(
    service: Annotated[PriorityService, Depends(get_priority_service)],
) -> list[PriorityResponse]:
    return [PriorityResponse.model_validate(p) for p in await service.get_all()]


@priority_router.post(
    "",
    response_model=PriorityResponse,
    status_code=201,
    dependencies=[Depends(require_admin)],
)
async def create_priority(
    data: PriorityCreate,
    service: Annotated[PriorityService, Depends(get_priority_service)],
) -> PriorityResponse:
    created = await service.create(name=data.name, sort_order=data.sort_order)
    return PriorityResponse.model_validate(created)


@priority_router.patch(
    "/{priority_id}",
    response_model=PriorityResponse,
    responses={404: {"model": ErrorResponse}},
    dependencies=[Depends(require_admin)],
)
async def update_priority(
    priority_id: int,
    data: PriorityUpdate,
    service: Annotated[PriorityService, Depends(get_priority_service)],
) -> PriorityResponse:
    updated = await service.update(priority_id, name=data.name, sort_order=data.sort_order)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Приоритет с id {priority_id} не найден")
    return PriorityResponse.model_validate(updated)


@priority_router.delete(
    "/{priority_id}",
    status_code=204,
    responses={404: {"model": ErrorResponse}},
    dependencies=[Depends(require_admin)],
)
async def delete_priority(
    priority_id: int,
    service: Annotated[PriorityService, Depends(get_priority_service)],
) -> None:
    deleted = await service.delete(priority_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Приоритет с id {priority_id} не найден")
