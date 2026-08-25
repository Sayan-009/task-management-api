from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from task_management_api.conversations.enums import ConversationStatus


class ConversationAssignee(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    email: EmailStr


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    task_id: UUID

    assignee: ConversationAssignee

    status: ConversationStatus

    created_at: datetime
    updated_at: datetime
    
    
class ConversationListResponse(BaseModel):
    items: list[ConversationResponse]

    page: int
    limit: int
    total: int
    total_pages: int