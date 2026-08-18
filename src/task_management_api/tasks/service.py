import math
from uuid import UUID
from sqlalchemy.orm import Session

from task_management_api.users.model import User
from task_management_api.tasks.model import Task, TaskAssignee
from task_management_api.tasks.repository import TaskRepository
from task_management_api.users.repository import UserRepository
from task_management_api.tasks.enums import (
    TaskPriority, 
    TaskStatus, 
    TaskOrder, 
    TaskSort,
    AssignedTaskSort
)
from task_management_api.tasks.schema import (
    TaskCreate,
    TaskUpdate,
    TaskStatusUpdate,
    TaskListResponse,
    TaskAssigneeCreate, 
    TaskDetailResponse,
    TaskOwnerResponse,
    TaskParticipantResponse,
    AssignedTaskResponse,
    AssignedTaskListResponse
)
from task_management_api.core.exceptions import (
    TaskNotFoundError,
    ForbiddenOperationError,
    NoUpdateFieldsError,
    AlreadyAssignedError,
    DuplicateAssigneeError,
    UserInactiveError,
    UserNotFoundError,
    AssignmentNotFoundError
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
    def get_task_details(
        session: Session,
        current_user: User,
        task_id: UUID,
    ) -> TaskDetailResponse:

        task = TaskRepository.get_by_id(session, task_id)

        if task is None:
            raise TaskNotFoundError("Task not found")

        is_owner = task.owner_id == current_user.id

        is_assignee = TaskRepository.get_by_task_user(
            session,
            task_id,
            current_user.id,
        ) is not None

        if not is_owner and not is_assignee:
            raise ForbiddenOperationError(
                "You don't have permission to access this task"
            )

        task_details = TaskRepository.get_task_with_assignees(
            session,
            task_id,
        )

        owner = TaskOwnerResponse(
            id=task_details.owner.id,
            name=task_details.owner.name,
            status=task_details.status,
        )

        assignees = [
            TaskParticipantResponse(
                user_id=assignment.user.id,
                name=assignment.user.name,
                status=assignment.status,
            )
            for assignment in task_details.assignees
        ]

        return TaskDetailResponse(
            id=task_details.id,
            title=task_details.title,
            description=task_details.description,
            priority=task_details.priority,
            status=task_details.status,
            owner=owner,
            assignees=assignees,
        )
    
    
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
        
        
    @staticmethod
    def assign_users(
        session: Session,
        task_id: UUID,
        owner_id: UUID,
        assignees: TaskAssigneeCreate,
    ) -> list[TaskAssignee]:

        task = TaskRepository.get_by_id(
            session,
            task_id,
        )

        if task is None:
            raise TaskNotFoundError("Task not found")

        if task.owner_id != owner_id:
            raise ForbiddenOperationError(
                "You don't have permission to assign users to this task"
            )

        assignee_ids = assignees.assignee_ids

        # Prevent duplicate IDs in the same request
        if len(assignee_ids) != len(set(assignee_ids)):
            raise DuplicateAssigneeError(
                "Duplicate users are not allowed"
            )

        for user_id in assignee_ids:

            user = UserRepository.get_by_id(
                session,
                user_id,
            )

            if user is None:
                raise UserNotFoundError(
                    f"User {user_id} not found"
                )

            if not user.is_active:
                raise UserInactiveError(
                    f"User {user_id} is inactive"
                )

            existing_assignment = TaskRepository.get_by_task_user(
                session,
                task_id,
                user_id,
            )

            if existing_assignment is not None:
                raise AlreadyAssignedError(
                    f"User {user_id} is already assigned to this task"
                )

        return TaskRepository.create_many(
            session,
            task_id,
            assignee_ids,
        )
    
    
    
    @staticmethod
    def delete_assignee(
        session: Session,
        current_user: User,
        assignee_id: UUID,
        task_id: UUID
    ) -> None:
        task = TaskRepository.get_by_id(session, task_id)
        if task is None:
            raise TaskNotFoundError(
                "Task not found"
            )
            
        if task.owner_id != current_user.id:
            raise ForbiddenOperationError(
                "you don't have permission to delete the assignees"
            )
            
        if UserRepository.get_by_id(session, assignee_id) is None:
            raise UserNotFoundError(
                f"assignee {assignee_id} not found"
            )
            
        task_assignee = TaskRepository.get_by_task_user(
            session,
            task_id,
            assignee_id,
        )
            
        if task_assignee is None:
            raise AssignmentNotFoundError(
                f"User {assignee_id} is not assigned to task {task_id}"
            )
            
        TaskRepository.delete_assignee(
            session, task_assignee
        )
        
        
    @staticmethod
    def update_my_status(
        session: Session,
        user_id: UUID,
        task_id: UUID,
        update_status: TaskStatusUpdate
    ) -> TaskAssignee:
        task = TaskRepository.get_by_id(session, task_id)
        if task is None:
            raise TaskNotFoundError(
                "Task not found"
            )
            
        task_assignee = TaskRepository.get_by_task_user(session, task_id, user_id)
        
        if task_assignee is None:
            raise ForbiddenOperationError(
                "you are not an assignee for this task"
            )
            
        return TaskRepository.update_assignee_status(
            session,
            task_assignee,
            update_status,
        )
        
        
        
    @staticmethod
    def get_assigned_tasks(
        session: Session,
        user_id: UUID,
        search: str | None = None,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        sort_by: AssignedTaskSort | None = None,
        order: TaskOrder = TaskOrder.ASC,
        page: int = 1,
        limit: int = 10,
    ) -> AssignedTaskListResponse:
    
        
        assignments, total = TaskRepository.get_tasks_by_assignee(
            session,
            user_id,
            search,
            status,
            priority,
            sort_by,
            order,
            page,
            limit
        )
        
        
        assigneed_tasks = [
            AssignedTaskResponse(
                id=assignment.task.id,
                title=assignment.task.title,
                description=assignment.task.description,
                priority=assignment.task.priority,
                status=assignment.task.status,
                my_status=assignment.status,
                owner=TaskOwnerResponse(
                    id=assignment.task.owner.id,
                    name=assignment.task.owner.name,
                    status=assignment.task.status,
                ),
            )
            for assignment in assignments
        ]
        
        total_pages = math.ceil(total / limit) if total > 0 else 0
        
        return AssignedTaskListResponse(
            assigned_tasks=assigneed_tasks,
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
        )
            
            
        