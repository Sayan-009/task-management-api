from uuid import UUID
from datetime import datetime
from pydantic import (
    BaseModel, 
    field_validator, 
    model_validator,
    EmailStr,
    ConfigDict,
    Field
)

from task_management_api.conversations.attachment_schema import (
    AttachmentResponse
)


class CreateMessageRequest(BaseModel):
    content: str | None = None
    reply_to_message_id: UUID | None = None
    attachment_ids: list[UUID] = Field(default_factory=list)

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None

    @model_validator(mode="after")
    def validate_message(self):
        if self.content is None and not self.attachment_ids:
            raise ValueError(
                "Message must contain text or at least one attachment"
            )

        if len(self.attachment_ids) != len(set(self.attachment_ids)):
            raise ValueError(
                "Attachment IDs must be unique"
            )

        return self


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
    content: str | None
    sender: SenderDetails
    is_deleted: bool
    
class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    conversation_id: UUID
    sender: SenderDetails
    content: str | None 
    reply_to: ReplyMessageResponse | None = None
    attachments: list[AttachmentResponse]
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