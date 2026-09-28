from uuid import UUID
from fastapi import UploadFile
from uuid import uuid4
from pathlib import Path
from sqlalchemy.orm import Session

from task_management_api.conversations.storage.file_storage import FileStorage
from task_management_api.conversations.attachment_repository import AttachmentRepository

from task_management_api.core.exceptions import (
    AttachmentNotFoundError,
    AttachmentNotAttachedError,
    ForbiddenOperationError
)

from task_management_api.conversations.attachment_model import MessageAttachment
from task_management_api.users.model import User

from task_management_api.conversations.storage import cloudinary_config


ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/gif",
}

ALLOWED_FILE_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/plain",
    "application/zip",
}

MAX_IMAGE_SIZE = 16 * 1024 * 1024
MAX_FILE_SIZE = 100 * 1024 * 1024


class AttachmentService:
    
    def __init__(self, storage: FileStorage):
        self.storage = storage
    
    async def upload_attachment(
        self,
        session: Session,
        file: UploadFile,
        user: User,
    ) -> MessageAttachment:
        allowed_types = ALLOWED_IMAGE_TYPES | ALLOWED_FILE_TYPES
        
        if file.content_type not in allowed_types:
            raise ValueError("Unsupported file type")
        
        
        if file.content_type in ALLOWED_IMAGE_TYPES:
            max_size = MAX_IMAGE_SIZE
        else:
            max_size = MAX_FILE_SIZE
        
        if not file.filename:
            raise ValueError("Filename is missing")
        
        stored_name = f"{uuid4()}{Path(file.filename).suffix}"
        
        if file.content_type in ALLOWED_IMAGE_TYPES:
            category = "images"
        else:
            category = "files"

        relative_path, file_size = await self.storage.save(
            file=file,
            stored_name=stored_name,
            category=category,
            max_size=max_size,
        )
                
        attachment = MessageAttachment(
            uploaded_by=user.id,
            file_name=file.filename,
            stored_name=stored_name,
            mime_type=file.content_type,
            file_size=file_size,
            file_path=relative_path,
        )
        
        try:
            created_attachment = AttachmentRepository.create(
                session,
                attachment
            )
        except Exception:
            await self.storage.delete(relative_path)
            raise

        return created_attachment
    
    
    
    async def upload_attachments(
        self,
        session: Session,
        files: list[UploadFile],
        user: User,
    ) -> list[MessageAttachment]:

        uploaded_attachments = []

        try:
            for file in files:
                attachment = await self.upload_attachment(
                    session,
                    file,
                    user,
                )

                uploaded_attachments.append(attachment)

            return uploaded_attachments

        except Exception:
            for attachment in uploaded_attachments:
                await self.storage.delete(attachment.file_path)

            raise
        
        
    def get_attachment_for_user(
        self,
        session: Session,
        current_user: User,
        attachment_id: UUID
    ) -> MessageAttachment :
        attachment = AttachmentRepository.get_with_message(
            session,
            attachment_id,
        )
        
        if attachment is None:
            raise AttachmentNotFoundError(
                "Attachment not found"
            )
            
        if attachment.message_id is None:
            raise AttachmentNotAttachedError(
                "Attachment is not attached with corresponding message"
            )
            
        is_owner = attachment.message.conversation.task.owner_id == current_user.id
        is_assignee = attachment.message.conversation.assignee_id == current_user.id
        
        if not is_owner and not is_assignee:
            raise ForbiddenOperationError(
                "You are not allowed to download or view this resource"
            )
            
            
        return attachment
    
    
    
        
        