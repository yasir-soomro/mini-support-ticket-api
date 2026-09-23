from enum import Enum
from pydantic import BaseModel, EmailStr, Field

class TicketStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"


class TicketCreate(BaseModel):
    customer_name: str = Field(..., min_length=1)
    customer_email: EmailStr
    subject: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)


class StatusUpdate(BaseModel):
    status: TicketStatus


class TicketResponse(BaseModel):
    id: int
    customer_name: str
    customer_email: str
    subject: str
    description: str
    status: TicketStatus

    model_config = {"from_attributes": True}
