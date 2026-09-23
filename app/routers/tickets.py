from fastapi import APIRouter, HTTPException, Depends
from app.models.ticket import TicketCreate, TicketResponse, TicketStatus, StatusUpdate
from app.dependencies.ticket_dependencies import get_ticket_service
from app.services.ticket_service import TicketService, TicketNotFoundError, InvalidTransitionError

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=TicketResponse, status_code=201)
async def create_ticket(payload: TicketCreate, service: TicketService = Depends(get_ticket_service)):
    ticket = await service.add_ticket(
        customer_name=payload.customer_name,
        customer_email=str(payload.customer_email),
        subject=payload.subject,
        description=payload.description,
    )
    return ticket


@router.get("", response_model=list[TicketResponse])
async def list_tickets(service: TicketService = Depends(get_ticket_service)):
    return await service.list_tickets()


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: int, service: TicketService = Depends(get_ticket_service)):
    ticket = await service.get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
async def update_status(ticket_id: int, payload: StatusUpdate, service: TicketService = Depends(get_ticket_service)):
    try:
        return await service.update_status(ticket_id, payload.status)
    except TicketNotFoundError:
        raise HTTPException(status_code=404, detail="Ticket not found")
    except InvalidTransitionError as e:
        raise HTTPException(status_code=422, detail=e.message)


@router.delete("/{ticket_id}", status_code=204)
async def delete_ticket(ticket_id: int, service: TicketService = Depends(get_ticket_service)):
    deleted = await service.delete_ticket(ticket_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ticket not found")
