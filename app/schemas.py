from enum import Enum
from pydantic import BaseModel, Field


class RequestStatus(str, Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class RequestCreate(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=3, max_length=2000)


class StatusUpdate(BaseModel):
    status: RequestStatus


class RequestOut(BaseModel):
    id: int
    title: str
    description: str
    status: RequestStatus
    created_at: str
    updated_at: str


class HistoryItem(BaseModel):
    old_status: str | None
    new_status: str
    changed_at: str
