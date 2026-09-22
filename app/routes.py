from fastapi import APIRouter, HTTPException
from app.models import TicketCreate, TicketResponse, TicketStatus, StatusUpdate
from app import store

router = APIRouter(prefix="/tickets", tags=["tickets"])

# Valid status transitions as defined in the specification
_VALID_TRANSITIONS: dict[TicketStatus, TicketStatus] = {
    TicketStatus.open: TicketStatus.in_progress,
    TicketStatus.in_progress: TicketStatus.resolved,
}


@router.post("", response_model=TicketResponse, status_code=201)
def create_ticket(payload: TicketCreate):
    ticket = store.add_ticket(
        customer_name=payload.customer_name,
        customer_email=str(payload.customer_email),
        subject=payload.subject,
        description=payload.description,
    )
    return ticket


@router.get("", response_model=list[TicketResponse])
def list_tickets():
    return store.list_tickets()


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int):
    ticket = store.get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
def update_status(ticket_id: int, payload: StatusUpdate):
    ticket = store.get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    current_status: TicketStatus = ticket["status"]
    allowed_next = _VALID_TRANSITIONS.get(current_status)

    if allowed_next != payload.status:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Invalid transition: '{current_status}' → '{payload.status}'. "
                f"Allowed transition from '{current_status}': "
                + (f"'{allowed_next}'" if allowed_next else "none (terminal state)")
            ),
        )

    return store.update_status(ticket_id, payload.status)


@router.delete("/{ticket_id}", status_code=204)
def delete_ticket(ticket_id: int):
    deleted = store.delete_ticket(ticket_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ticket not found")
