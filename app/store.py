from typing import Optional
from app.models import TicketStatus

# In-memory storage
_store: dict[int, dict] = {}
_counter: int = 0


def _next_id() -> int:
    global _counter
    _counter += 1
    return _counter


def add_ticket(customer_name: str, customer_email: str, subject: str, description: str) -> dict:
    ticket_id = _next_id()
    ticket = {
        "id": ticket_id,
        "customer_name": customer_name,
        "customer_email": customer_email,
        "subject": subject,
        "description": description,
        "status": TicketStatus.open,
    }
    _store[ticket_id] = ticket
    return ticket


def get_ticket(ticket_id: int) -> Optional[dict]:
    return _store.get(ticket_id)


def list_tickets() -> list[dict]:
    return list(_store.values())


def update_status(ticket_id: int, new_status: TicketStatus) -> Optional[dict]:
    ticket = _store.get(ticket_id)
    if ticket is None:
        return None
    ticket["status"] = new_status
    return ticket


def delete_ticket(ticket_id: int) -> bool:
    if ticket_id not in _store:
        return False
    del _store[ticket_id]
    return True


def clear() -> None:
    """Reset store and counter — used by tests only."""
    global _counter
    _store.clear()
    _counter = 0
