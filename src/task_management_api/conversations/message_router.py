from uuid import UUID
from fastapi import APIRouter, status, Depends, HTTPException, Query

from sqlalchemy.orm import (
    Session
)


from task_management_api.core.dependencies import get_current_user
from task_management_api.db.session import get_db

from task_management_api.users.model import User
from task_management_api.conversations.message_service import MessageService
from task_management_api.conversations.message_schema import (
    MessageResponse,
    MessageBody,
    MessageListResponse
)
from task_management_api.core.exceptions import (
    TaskNotFoundError,
    ConversationNotFoundError,
    ForbiddenOperationError,
    MessageNotFoundError,
    MessageAlreadyDeletedError,
    MessageEditLimitExceededError
)


message_router = APIRouter(
    prefix="/conversations",
    tags=["messages"]
)


@message_router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED
)
def create_message(
    conversation_id: UUID,
    message: MessageBody,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> MessageResponse:
    try:
        message = MessageService.create_message(
            session,
            current_user,
            conversation_id,
            message
        )
        
        session.commit()
        
        return message
    
    except TaskNotFoundError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc
      
    except ConversationNotFoundError as exc:
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
        
        
        
@message_router.patch(
    "/{conversation_id}/messages/{message_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK
)
def update_message(
    conversation_id: UUID,
    message_id: UUID,
    updated_message: MessageBody,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> MessageResponse:
    try:
        message = MessageService.update_message(
            session,
            current_user,
            updated_message,
            conversation_id,
            message_id
        )
        
        session.commit()
        return message
    
    except ValueError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc)
        ) from exc
    
    except ConversationNotFoundError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc
        
    except MessageNotFoundError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc
        
        
    except MessageAlreadyDeletedError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        ) from exc
        
    except ForbiddenOperationError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc)
        ) from exc
        
    except ForbiddenOperationError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        ) from exc
    
    except MessageEditLimitExceededError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        ) from exc
    
    
@message_router.delete(
    "/{conversation_id}/messages/{message_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_message(
    conversation_id: UUID,
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> None:
    try:
        MessageService.delete_message(
            session,
            current_user,
            conversation_id,
            message_id
        )
        
        session.commit()
    
    except ConversationNotFoundError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc
        
    except MessageNotFoundError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc
        
        
    except MessageAlreadyDeletedError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        ) from exc
        
    except ForbiddenOperationError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc)
        ) from exc
        
        
@message_router.get(
    "/{conversation_id}/messages",
    response_model=MessageListResponse,
    status_code=status.HTTP_200_OK
)
def get_messages(
    conversation_id: UUID,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> MessageListResponse:
    try:
        messages = MessageService.get_messages(
            session,
            current_user,
            conversation_id,
            page,
            limit
        )
        
        return messages
    
    except ConversationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc
        
    except ForbiddenOperationError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc)
        ) from exc
    
    