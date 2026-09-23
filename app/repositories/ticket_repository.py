from typing import Optional
from app.models.ticket import TicketStatus

class TicketRepository:
    def __init__(self):
        self._store: dict[int, dict] = {}
        self._counter: int = 0
    
    def _next_id(self) -> int:
        self._counter += 1
        return self._counter

    async def add(self, ticket_data: dict) -> dict:
        ticket_id = self._next_id()
        ticket_data["id"] = ticket_id
        self._store[ticket_id] = ticket_data
        return ticket_data

    async def get(self, ticket_id: int) -> Optional[dict]:
        return self._store.get(ticket_id)

    async def list_all(self) -> list[dict]:
        return list(self._store.values())

    async def update(self, ticket_id: int, ticket_data: dict) -> Optional[dict]:
        if ticket_id in self._store:
            self._store[ticket_id] = ticket_data
            return ticket_data
        return None

    async def delete(self, ticket_id: int) -> bool:
        if ticket_id not in self._store:
            return False
        del self._store[ticket_id]
        return True

    def clear(self) -> None:
        self._store.clear()
        self._counter = 0

# Create a singleton instance for in-memory persistence across requests
_ticket_repository = TicketRepository()

def get_ticket_repository() -> TicketRepository:
    return _ticket_repository
