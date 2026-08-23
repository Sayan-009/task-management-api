from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator

class CreateComment(BaseModel):
    content: str = Field(
        min_length=1,
        max_length=5000
    )
    
    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Comment content cannot be empty or contain only whitespace"
            )

        return value
    
class UpdateComment(BaseModel):
    content: str = Field(
        min_length=1,
        max_length=5000
    )
    
    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Comment content cannot be empty or contain only whitespace"
            )

        return value
    
class AuthorDetails(BaseModel):
    id: UUID
    name: str
    email: EmailStr


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    content: str
    task_id: UUID
    author: AuthorDetails

    is_edited: bool
    edited_at: datetime | None = None

    is_deleted: bool
    deleted_at: datetime | None = None

    created_at: datetime
    updated_at: datetime


class CommentListResponse(BaseModel):
    items: list[CommentResponse]

    page: int
    limit: int

    total: int
    total_pages: int