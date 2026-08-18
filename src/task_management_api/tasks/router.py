from uuid import UUID
from fastapi import Query
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, HTTPException


from task_management_api.db.session import get_db
from task_management_api.core.dependencies import get_current_user
from task_management_api.users.model import User
from task_management_api.tasks.model import Task
from task_management_api.tasks.service import TaskService
from task_management_api.tasks.enums import (TaskPriority, TaskStatus, TaskOrder, TaskSort, AssignedTaskSort)
from task_management_api.tasks.schema import (
    TaskCreate, TaskResponse, TaskUpdate, TaskStatusUpdate, TaskListResponse,
    TaskAssigneeCreate, TaskAssigneeResponse, TaskDetailResponse, AssignedTaskResponse,
    AssignedTaskListResponse
)
from task_management_api.core.exceptions import (
    TaskNotFoundError,
    ForbiddenOperationError,
    NoUpdateFieldsError,
    DuplicateAssigneeError,
    UserNotFoundError,
    UserInactiveError,
    AlreadyAssignedError,
    AssignmentNotFoundError
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
    
    
@router.get("/", response_model=TaskListResponse, status_code=status.HTTP_200_OK)
def get_user_tasks(
    search: str | None = None,
    status: TaskStatus | None = Query(default=None),
    priority: TaskPriority | None = Query(default=None),
    sort_by: TaskSort | None = None,
    order: TaskOrder = TaskOrder.ASC,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
    page: int = 1,
    limit: int = 10,
) -> TaskListResponse:
     
    return TaskService.get_user_tasks(
        session, 
        current_user.id,
        search,
        status,
        priority,
        sort_by,
        order,
        page,
        limit
    )
    
    
@router.get("/assigned", response_model=AssignedTaskListResponse, status_code=status.HTTP_200_OK)
def get_assigned_task(
    search: str | None = Query(default=None),
    status: TaskStatus | None = Query(default=None),
    priority: TaskPriority | None = Query(default=None),
    sort_by: AssignedTaskSort | None = Query(default=None),
    order: TaskOrder = Query(default=TaskOrder.ASC),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> AssignedTaskListResponse:
     
    return TaskService.get_assigned_tasks(
        session, 
        current_user.id,
        search,
        status,
        priority,
        sort_by,
        order,
        page,
        limit
    )


@router.get("/{task_id}", response_model=TaskDetailResponse, status_code=status.HTTP_200_OK)
def get_task_details(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> TaskDetailResponse:
    try:
        task_details = TaskService.get_task_details(
            session,
            current_user,
            task_id
        )
        
        return task_details
    
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
        
        
@router.patch("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def update_task(
    task_id: UUID,
    update_task: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> TaskResponse:
    try:
        task = TaskService.update_task(
            session, current_user, task_id, update_task
        )
        
        session.commit()
        
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
        
    except NoUpdateFieldsError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        ) from exc
        
        
@router.patch("/{task_id}/status", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def task_status_update(
    task_id: UUID,
    task_status: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> TaskResponse:
    try:
        task = TaskService.status_update(
            session,
            current_user,
            task_id,
            task_status=task_status,
        )
        
        session.commit()
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
        
        

@router.delete("/{task_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> None:
    try:
        TaskService.delete_task(
            session, current_user, task_id,
        )
        
        session.commit()
    
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
        
        

@router.post(
    "/{task_id}/assignees",
    response_model=list[TaskAssigneeResponse],
    status_code=status.HTTP_201_CREATED,
)
def assign_users(
    task_id: UUID,
    assignees: TaskAssigneeCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> list[TaskAssigneeResponse]:
    try:
        task_assignments = TaskService.assign_users(
            session,
            task_id,
            current_user.id,
            assignees,
        )
        
        session.commit()
        
        return task_assignments
    
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
        
        
    except DuplicateAssigneeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        ) from exc
            
            
            
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc
        
        
    except UserInactiveError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        ) from exc
        
        
    except AlreadyAssignedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc)
        ) from exc
        
        
        
@router.delete('/{task_id}/assignees/{assignee_id}', response_model=None, status_code=status.HTTP_204_NO_CONTENT)
def delete_assignee(
    task_id: UUID,
    assignee_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> None:
    try:
        TaskService.delete_assignee(
            session,
            current_user,
            assignee_id,
            task_id,
        )
        
        session.commit()
        
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


    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc
        
        
    except AssignmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
        
        
        
@router.patch("/{task_id}/my-status", response_model=TaskAssigneeResponse, status_code=status.HTTP_200_OK)
def update_my_status(
    task_id: UUID,
    update_status: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> TaskAssigneeResponse:
    try:
        task_assignee = TaskService.update_my_status(
            session,
            current_user.id,
            task_id,
            update_status
        )
        
        session.commit()
        
        return task_assignee
    
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
        
        

