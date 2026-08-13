from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, HTTPException


from task_management_api.db.session import get_db
from task_management_api.core.dependencies import get_current_user
from task_management_api.users.model import User
from task_management_api.tasks.model import Task
from task_management_api.tasks.service import TaskService
from task_management_api.tasks.schema import (
    TaskCreate, TaskResponse
)
from task_management_api.core.exceptions import (
    TaskNotFoundError,
    ForbiddenOperationError
)


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> TaskResponse:
    try:
        created_task = TaskService.create_task(
            session,
            task,
            owner_id=current_user.id,
        )

        session.commit()

        return created_task

    except Exception:
        session.rollback()
        raise
    
    
@router.get("/", response_model=list[TaskResponse], status_code=status.HTTP_200_OK)
def get_user_tasks(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> list[TaskResponse]:
     
    return TaskService.get_user_tasks(session, current_user.id)


@router.get("/{task_id}", response_model=TaskResponse | None, status_code=status.HTTP_200_OK)
def get_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> TaskResponse | None:
    try:
        task = TaskService.get_task(
            session,
            current_user,
            task_id
        )
        
        return task
    
    except TaskNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ForbiddenOperationError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    