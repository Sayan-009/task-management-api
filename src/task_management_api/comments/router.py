from uuid import UUID

from fastapi import APIRouter, status, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from task_management_api.core.dependencies import get_current_user
from task_management_api.db.session import get_db


from task_management_api.users.model import User
from task_management_api.comments.service import CommentService


from task_management_api.core.exceptions import (
    TaskNotFoundError,
    CommentNotFoundError,
    ForbiddenOperationError,
    UpdateSameContentError
)
from task_management_api.comments.schema import (
    CreateComment,
    CommentResponse,
    UpdateComment,
    CommentListResponse
)


task_router = APIRouter(
    prefix="/tasks",
    tags=["comments"]
)

comment_router = APIRouter(
    prefix="/comments",
    tags=["comments"]
)

@task_router.post("/{task_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    task_id: UUID,
    comment_data: CreateComment,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> CommentResponse:
    
    try:
        comment = CommentService.create_comment(
            session,
            task_id,
            current_user,
            comment_data,
        )
        
        session.commit()
        
        return comment

    except TaskNotFoundError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc
        
    except ForbiddenOperationError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc)
        ) from exc
        
        
@task_router.get("/{task_id}/comments", response_model=CommentListResponse, status_code=status.HTTP_200_OK)
def get_comments(
    task_id: UUID,
    page: int = Query(
        default=1,
        ge=1
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100
    ),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> CommentListResponse:

    try:
        return CommentService.get_comments(
            session=session,
            current_user=current_user,
            task_id=task_id,
            page=page,
            limit=limit,
        )

    except TaskNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc

    except ForbiddenOperationError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc)
        ) from exc
        
        
@comment_router.patch("/{comment_id}", response_model=CommentResponse, status_code=status.HTTP_200_OK)
def update_comment(
    comment_id: UUID,
    update_data: UpdateComment,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> CommentResponse:
    try:
        updated_comment = CommentService.update_comment(
            session,
            comment_id,
            current_user,
            update_data
        )
        
        session.commit()
        
        return updated_comment
 
    except CommentNotFoundError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc       
    
            
    except ForbiddenOperationError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc)
        ) from exc
        
    except UpdateSameContentError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        ) from exc
        
        
@comment_router.delete("/{comment_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> None:
    
    try:
        CommentService.delete_comment(
            session,
            comment_id,
            current_user
        )
        
        session.commit()
        
    except CommentNotFoundError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc       
    
            
    except ForbiddenOperationError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc)
        ) from exc
          