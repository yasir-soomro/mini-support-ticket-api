from fastapi import Depends
from app.services.ticket_service import TicketService
from app.repositories.ticket_repository import TicketRepository, get_ticket_repository

def get_ticket_service(repository: TicketRepository = Depends(get_ticket_repository)) -> TicketService:
    return TicketService(repository)
