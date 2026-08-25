from uuid import UUID

from fastapi import (
    APIRouter,
    status,
    Depends,
    Query,
    HTTPException
)
from sqlalchemy.orm import Session

from task_management_api.db.session import get_db
from task_management_api.core.dependencies import get_current_user
from task_management_api.users.model import User

from task_management_api.conversations.conversation_service import (
    ConversationService
)
from task_management_api.conversations.conversation_schema import (
    ConversationListResponse
)
from task_management_api.core.exceptions import (
    TaskNotFoundError,
    ForbiddenOperationError
)


conv_router = APIRouter(
    prefix="/tasks",
    tags=["conversations"]
)


@conv_router.get(
    "/{task_id}/conversations",
    response_model=ConversationListResponse,
    status_code=status.HTTP_200_OK
)
def get_conversations(
    task_id: UUID,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> ConversationListResponse:

    try:
        return ConversationService.get_conversation(
            session=session,
            current_user=current_user,
            task_id=task_id,
            page=page,
            limit=limit
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