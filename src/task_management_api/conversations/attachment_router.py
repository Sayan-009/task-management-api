from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, status, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from task_management_api.db.session import get_db
from task_management_api.core.dependencies import get_current_user
from task_management_api.conversations.dependencies import get_attachment_service

from task_management_api.users.model import User
from task_management_api.conversations.attachment_service import AttachmentService
from task_management_api.conversations.attachment_schema import AttachmentResponse

from task_management_api.core.exceptions import (
    AttachmentNotAttachedError,
    AttachmentNotFoundError,
    ForbiddenOperationError
)


attachment_router = APIRouter(
    prefix="/attachments",
    tags=["attachments"]
)


@attachment_router.post(
    "/upload",
    response_model=list[AttachmentResponse],
    status_code=status.HTTP_201_CREATED,
)
async def file_upload(
    files: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    attachment_service: AttachmentService = Depends(get_attachment_service),
    session: Session = Depends(get_db)
) -> list[AttachmentResponse]:
    try:
        uploaded_attachments = await attachment_service.upload_attachments(
            session,
            files,
            current_user,
        )

        session.commit()

        return uploaded_attachments
    
    except ValueError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
        
    
@attachment_router.get("/{attachment_id}")
async def get_attachment(
    attachment_id: UUID,
    current_user: User = Depends(get_current_user),
    attachment_service: AttachmentService = Depends(get_attachment_service),
    session: Session = Depends(get_db),
):
    try:
        attachment = attachment_service.get_attachment_for_user(
            session,
            current_user,
            attachment_id,
        )

        file_path = attachment_service.storage.get_path(
            attachment.file_path
        )

        if not file_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found",
            )

        disposition = (
            "inline"
            if attachment.mime_type.startswith("image/")
            else "attachment"
        )

        return FileResponse(
            path=file_path,
            media_type=attachment.mime_type,
            filename=attachment.file_name,
            content_disposition_type=disposition,
        )

    except AttachmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except AttachmentNotAttachedError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except ForbiddenOperationError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )