from fastapi import APIRouter, status, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from task_management_api.db.session import get_db
from task_management_api.core.dependencies import get_current_user
from task_management_api.conversations.dependencies import get_attachment_service


from task_management_api.users.model import User
from task_management_api.conversations.attachment_service import AttachmentService
from task_management_api.conversations.attachment_schema import AttachmentResponse

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