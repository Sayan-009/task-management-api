from uuid import UUID
from datetime import datetime
from pydantic import (
    BaseModel, 
    field_validator, 
    EmailStr,
    ConfigDict
)


class CreateMessageRequest(BaseModel):
    content: str
    reply_to_message_id: UUID | None = None

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Message content cannot be empty or contain only whitespace"
            )

        return value


class UpdateMessageRequest(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Message content cannot be empty or contain only whitespace"
            )

        return value
    
class SenderDetails(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    
class ReplyMessageResponse(BaseModel):
    id: UUID
    content: str
    sender: SenderDetails
    is_deleted: bool
    
class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    conversation_id: UUID
    sender: SenderDetails
    content: str
    reply_to: ReplyMessageResponse | None = None
    is_read: bool
    read_at: datetime | None
    is_edited: bool
    edited_at: datetime | None
    is_deleted: bool
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime
    
    
class MessageListResponse(BaseModel):
    items: list[MessageResponse]
    page: int
    limit: int
    total: int
    total_pages: int