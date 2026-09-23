from typing import Optional
from app.models.ticket import TicketStatus, TicketCreate, StatusUpdate

_VALID_TRANSITIONS: dict[TicketStatus, TicketStatus] = {
    TicketStatus.open: TicketStatus.in_progress,
    TicketStatus.in_progress: TicketStatus.resolved,
}


class TicketNotFoundError(Exception):
    pass


class InvalidTransitionError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class TicketService:
    def __init__(self, repository):
        self.repository = repository

    async def add_ticket(self, customer_name: str, customer_email: str, subject: str, description: str) -> dict:
        ticket_data = {
            "customer_name": customer_name,
            "customer_email": customer_email,
            "subject": subject,
            "description": description,
            "status": TicketStatus.open,
        }
        return await self.repository.add(ticket_data)

    async def get_ticket(self, ticket_id: int) -> Optional[dict]:
        return await self.repository.get(ticket_id)

    async def list_tickets(self) -> list[dict]:
        return await self.repository.list_all()

    async def update_status(self, ticket_id: int, new_status: TicketStatus) -> dict:
        ticket = await self.repository.get(ticket_id)
        if ticket is None:
            raise TicketNotFoundError()
        
        current_status: TicketStatus = ticket["status"]
        allowed_next = _VALID_TRANSITIONS.get(current_status)

        if allowed_next != new_status:
            msg = (
                f"Invalid transition: '{current_status}' → '{new_status}'. "
                f"Allowed transition from '{current_status}': "
                + (f"'{allowed_next}'" if allowed_next else "none (terminal state)")
            )
            raise InvalidTransitionError(msg)

        ticket["status"] = new_status
        await self.repository.update(ticket_id, ticket)
        return ticket

    async def delete_ticket(self, ticket_id: int) -> bool:
        return await self.repository.delete(ticket_id)
