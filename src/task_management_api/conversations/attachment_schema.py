from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AttachmentResponse(BaseModel):
    id: UUID
    file_name: str
    mime_type: str
    file_size: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)