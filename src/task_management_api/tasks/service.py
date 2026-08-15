import math
from uuid import UUID
from sqlalchemy.orm import Session


from task_management_api.users.model import User
from task_management_api.tasks.model import Task
from task_management_api.tasks.repository import TaskRepository
from task_management_api.tasks.enums import (TaskPriority, TaskStatus, TaskOrder, TaskSort)
from task_management_api.tasks.schema import (
    TaskCreate,
    TaskUpdate,
    TaskStatusUpdate,
    TaskListResponse
)
from task_management_api.core.exceptions import (
    TaskNotFoundError,
    ForbiddenOperationError,
    NoUpdateFieldsError
)



class TaskService:
    
    @staticmethod
    def create_task(
        session: Session,
        task: TaskCreate,
        owner_id: UUID,
    ) -> Task:
        return TaskRepository.create(
            session,
            owner_id,
            task
        )
        
    @staticmethod
    def get_user_tasks(
        session: Session,
        owner_id: UUID,
        search: str | None = None,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        sort_by: TaskSort | None = None,
        order: TaskOrder = TaskOrder.ASC,
        page: int = 1,
        limit: int = 10,
    ) -> TaskListResponse:
        
        tasks, total = TaskRepository.get_by_owner(
            session,
            owner_id,
            search,
            status,
            priority,
            sort_by,
            order,
            page,
            limit
        )
        
        total_pages = math.ceil(total / limit) if total > 0 else 0
        
        return TaskListResponse(
            tasks=tasks,
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
        )
        
        
    @staticmethod
    def get_task(
        session: Session,
        current_user: User,
        task_id: UUID,
    ) -> Task | None:
        task = TaskRepository.get_by_id(session, task_id)
        if task is None:
            raise TaskNotFoundError("Task not found")
        
        if task.owner_id != current_user.id:
            raise ForbiddenOperationError("You don't have permission to access this task")
        
        return TaskRepository.get_by_id(session, task_id)
    
    
    @staticmethod
    def update_task(
        session: Session,
        current_user: User,
        task_id: UUID,
        update_task: TaskUpdate,
    ) -> Task:
        task = TaskRepository.get_by_id(session, task_id)
        
        if task is None:
            raise TaskNotFoundError("Task not found")
        
        if current_user.id != task.owner_id:
            raise ForbiddenOperationError("You don't have permission to update this task")
        
        updates = update_task.model_dump(exclude_unset=True)
        
        if not updates:
            raise NoUpdateFieldsError("At least one field is required to update the task")
        
        return TaskRepository.update(
            session,
            task,
            updates,
        )
        
        
    @staticmethod
    def status_update(
        session: Session,
        current_user: User,
        task_id: UUID,
        task_status: TaskStatusUpdate,
    ) -> Task:
        task = TaskRepository.get_by_id(session, task_id)
                
        if task is None:
            raise TaskNotFoundError("Task not found")
                
        if current_user.id != task.owner_id:
            raise ForbiddenOperationError("You don't have permission to update this task status")
        
        return TaskRepository.status_update(
            session,
            task,
            task_status
        )
    
    
    @staticmethod
    def delete_task(
        session: Session,
        current_user: User,
        task_id: UUID,
    ) -> None:
        task = TaskRepository.get_by_id(session, task_id)
        
        if task is None:
            raise TaskNotFoundError("Task not found")
        
        if current_user.id != task.owner_id:
            raise ForbiddenOperationError("You don't have permission to delete this task")
        
        TaskRepository.delete(
            session,
            task,
        )    