from uuid import UUID
from fastapi import Query
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status

from task_management_api.db.session import get_db
from task_management_api.core.dependencies import get_current_user
from task_management_api.users.model import User
from task_management_api.tasks.service import TaskService
from task_management_api.tasks.enums import (TaskPriority, TaskStatus, TaskOrder, TaskSort, AssignedTaskSort)
from task_management_api.tasks.schema import (
    TaskCreate, 
    TaskResponse, 
    TaskUpdate, 
    TaskStatusUpdate, 
    TaskListResponse,
    TaskAssigneeCreate, 
    TaskAssigneeResponse, 
    TaskDetailResponse, 
    AssignedTaskListResponse,
    TaskActivityListResponse
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
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
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
    
    
@router.get(
    "/deleted",
    response_model=TaskListResponse,
    status_code=status.HTTP_200_OK,
)
def get_deleted_tasks(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> TaskListResponse:

    return TaskService.get_deleted_tasks(
        session,
        current_user,
        page,
        limit,
    )


@router.get("/{task_id}", response_model=TaskDetailResponse, status_code=status.HTTP_200_OK)
def get_task_details(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> TaskDetailResponse:
    task_details = TaskService.get_task_details(
        session,
        current_user,
        task_id
    )
        
    return task_details
        
        
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
    
    except Exception:
        session.rollback()
        raise
        
        
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
    
    except Exception:
        session.rollback()
        raise  
        


@router.delete(
    "/{task_id}/permanent",
    status_code=status.HTTP_204_NO_CONTENT,
)
def hard_delete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> None:

    try:
        TaskService.hard_delete_task(
            session,
            current_user,
            task_id,
        )

        session.commit()

    except Exception:
        session.rollback()
        raise
        
        
@router.delete("/{task_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT,)
def soft_delete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> None:
    try:
        TaskService.soft_delete_task(
            session,
            current_user,
            task_id,
        )

        session.commit()

    except Exception:
        session.rollback()
        raise
        
        
@router.post("/{task_id}/restore", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def restore_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> TaskResponse:

    try:
        task = TaskService.restore_task(
            session,
            current_user,
            task_id,
        )

        session.commit()

        return task

    except Exception:
        session.rollback()
        raise
        

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
    
    except Exception:
        session.rollback()
        raise
        
        
        
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
        
    except Exception:
        session.rollback()
        raise   
        
        
        
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
    
    except Exception:
        session.rollback()
        raise
        
        
        
@router.delete(
    "/{task_id}/my-assignment",
    status_code=status.HTTP_204_NO_CONTENT,
)
def leave_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> None:

    try:
        TaskService.leave_task(
            session,
            current_user,
            task_id,
        )

        session.commit()

    except Exception:
        session.rollback()
        raise
        
        
        
@router.get("/{task_id}/activities", response_model=TaskActivityListResponse, status_code=status.HTTP_200_OK)
def get_task_activities(
    task_id: UUID,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> TaskActivityListResponse:
    return TaskService.get_task_activities(
        session,
        task_id,
        current_user,
        page, 
        limit,
    )

