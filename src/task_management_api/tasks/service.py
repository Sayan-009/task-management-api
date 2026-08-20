import math
from uuid import UUID
from sqlalchemy.orm import Session

from task_management_api.users.model import User
from task_management_api.tasks.model import Task, TaskAssignee
from task_management_api.tasks.repository import TaskRepository
from task_management_api.users.repository import UserRepository
from task_management_api.users.enums import UserRole
from task_management_api.tasks.enums import (
    TaskPriority, 
    TaskStatus, 
    TaskOrder, 
    TaskSort,
    AssignedTaskSort,
    TaskActivityType
)
from task_management_api.tasks.schema import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskStatusUpdate,
    TaskListResponse,
    TaskAssigneeCreate, 
    TaskDetailResponse,
    TaskOwnerResponse,
    TaskParticipantResponse,
    AssignedTaskResponse,
    AssignedTaskListResponse,
    ActivityUserResponse,
    TaskActivityResponse,
    TaskActivityListResponse
)
from task_management_api.core.exceptions import (
    TaskNotFoundError,
    ForbiddenOperationError,
    NoUpdateFieldsError,
    AlreadyAssignedError,
    DuplicateAssigneeError,
    UserInactiveError,
    UserNotFoundError,
    AssignmentNotFoundError,
    TaskAlreadyDeletedError,
    TaskNotDeletedError
)



class TaskService:
    
    @staticmethod
    def create_task(
        session: Session,
        task: TaskCreate,
        owner_id: UUID,
    ) -> Task:
        task = TaskRepository.create(
            session,
            owner_id,
            task
        )
        
        TaskRepository.create_activity(
            session=session,
            task_id=task.id,
            user_id=owner_id,
            action=TaskActivityType.CREATED,
        )
        
        return task
        
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

        task = TaskRepository.get_active_by_id(session, task_id)

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
        task = TaskRepository.get_active_by_id(session, task_id)
        
        if task is None:
            raise TaskNotFoundError("Task not found")
        
        if current_user.id != task.owner_id:
            raise ForbiddenOperationError("You don't have permission to update this task")
        
        updates = update_task.model_dump(exclude_unset=True)
        
        if not updates:
            raise NoUpdateFieldsError("At least one field is required to update the task")
        
        old_title = task.title
        old_description = task.description
        old_priority = task.priority
        
        updated_task = TaskRepository.update(
            session,
            task,
            updates,
        )
        
        # Record title change
        if old_title != updated_task.title:
            TaskRepository.create_activity(
                session=session,
                task_id=updated_task.id,
                user_id=current_user.id,
                action=TaskActivityType.UPDATED,
                field="title",
                old_value=old_title,
                new_value=updated_task.title,
            )

        # Record description change
        if old_description != updated_task.description:
            TaskRepository.create_activity(
                session=session,
                task_id=updated_task.id,
                user_id=current_user.id,
                action=TaskActivityType.UPDATED,
                field="description",
                old_value=old_description,
                new_value=updated_task.description,
            )

        # Record priority change
        if old_priority != updated_task.priority:
            TaskRepository.create_activity(
                session=session,
                task_id=updated_task.id,
                user_id=current_user.id,
                action=TaskActivityType.UPDATED,
                field="priority",
                old_value=old_priority.value,
                new_value=updated_task.priority.value,
            )
        
        return updated_task
        
        
    @staticmethod
    def status_update(
        session: Session,
        current_user: User,
        task_id: UUID,
        task_status: TaskStatusUpdate,
    ) -> Task:
        task = TaskRepository.get_active_by_id(session, task_id)
                
        if task is None:
            raise TaskNotFoundError("Task not found")
                
        if current_user.id != task.owner_id:
            raise ForbiddenOperationError("You don't have permission to update this task status")
        
        old_status = task.status
        
        updated_task = TaskRepository.status_update(
            session,
            task,
            task_status
        )
        
        if old_status != updated_task.status:
            TaskRepository.create_activity(
                session=session,
                task_id=task_id,
                user_id=current_user.id,
                action=TaskActivityType.STATUS_CHANGED,
                field="status",
                old_value=old_status.value,
                new_value=updated_task.status.value,
            )
        
        return updated_task
    
    
    @staticmethod
    def delete_task(
        session: Session,
        current_user: User,
        task_id: UUID,
    ) -> None:
        task = TaskRepository.get_active_by_id(session, task_id)
        
        if task is None:
            raise TaskNotFoundError("Task not found")
        
        if current_user.id != task.owner_id:
            raise ForbiddenOperationError("You don't have permission to delete this task")
        
        TaskRepository.delete(
            session,
            task,
        )
        
        
    @staticmethod
    def soft_delete_task(
        session: Session,
        current_user: User,
        task_id: UUID,
    ) -> None:

        task = TaskRepository.get_active_by_id(
            session,
            task_id,
        )

        if task is None:
            raise TaskNotFoundError(
                "Task not found"
            )

        if task.owner_id != current_user.id:
            raise ForbiddenOperationError(
                "You don't have permission to delete this task"
            )

        if task.is_deleted:
            raise TaskAlreadyDeletedError(
                "Task is already deleted"
            )

        TaskRepository.soft_delete_task(
            session,
            task,
        )

        TaskRepository.create_activity(
            session=session,
            task_id=task_id,
            user_id=current_user.id,
            action=TaskActivityType.DELETED,
            field=None,
            old_value="false",
            new_value="true",
        )
        
    @staticmethod
    def hard_delete_task(
        session: Session,
        current_user: User,
        task_id: UUID,
    ) -> None:

        if current_user.role != UserRole.ADMIN:
            raise ForbiddenOperationError(
                "Only admins can permanently delete tasks"
            )

        task = TaskRepository.get_by_id(
            session,
            task_id,
        )

        if task is None:
            raise TaskNotFoundError(
                "Task not found"
            )

        if not task.is_deleted:
            raise TaskNotDeletedError(
                "Only deleted tasks can be permanently deleted"
            )

        TaskRepository.hard_delete_task(
            session,
            task,
        )
        
        
    @staticmethod
    def restore_task(
        session: Session,
        current_user: User,
        task_id: UUID,
    ) -> Task:

        task = TaskRepository.get_by_id(
            session,
            task_id,
        )

        if task is None:
            raise TaskNotFoundError(
                "Task not found"
            )

        is_owner = task.owner_id == current_user.id
        is_admin = current_user.role == UserRole.ADMIN

        if not is_owner and not is_admin:
            raise ForbiddenOperationError(
                "You don't have permission to restore this task"
            )

        if not task.is_deleted:
            raise TaskNotDeletedError(
                "Task is not deleted"
            )

        TaskRepository.restore_task(
            session,
            task,
        )

        TaskRepository.create_activity(
            session=session,
            task_id=task_id,
            user_id=current_user.id,
            action=TaskActivityType.RESTORED,
            field=None,
            old_value=None,
            new_value=None,
        )

        return task
        
        
    @staticmethod
    def assign_users(
        session: Session,
        task_id: UUID,
        owner_id: UUID,
        assignees: TaskAssigneeCreate,
    ) -> list[TaskAssignee]:

        task = TaskRepository.get_active_by_id(
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

        assignments = TaskRepository.create_many(
            session,
            task_id,
            assignee_ids,
        )
        
        
        # Create activity for each newly assigned user
        for assignment in assignments:
            TaskRepository.create_activity(
                session=session,
                task_id=task_id,
                user_id=owner_id,
                action=TaskActivityType.ASSIGNEE_ADDED,
                field="assignee",
                old_value=None,
                new_value=str(assignment.user_id),
            )
        
        return assignments
    
    
    @staticmethod
    def leave_task(
        session: Session,
        current_user: User,
        task_id: UUID,
    ) -> None:

        task = TaskRepository.get_active_by_id(
            session,
            task_id,
        )

        if task is None:
            raise TaskNotFoundError(
                "Task not found"
            )

        task_assignee = TaskRepository.get_by_task_user(
            session,
            task_id,
            current_user.id,
        )

        if task_assignee is None:
            raise AssignmentNotFoundError(
                "You are not assigned to this task"
            )

        TaskRepository.create_activity(
            session=session,
            task_id=task_id,
            user_id=current_user.id,
            action=TaskActivityType.ASSIGNEE_REMOVED,
            field="assignee",
            old_value=str(current_user.id),
            new_value=None,
        )

        TaskRepository.delete_assignee(
            session,
            task_assignee,
        )
    
    
    
    @staticmethod
    def delete_assignee(
        session: Session,
        current_user: User,
        assignee_id: UUID,
        task_id: UUID
    ) -> None:
        task = TaskRepository.get_active_by_id(session, task_id)
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
            
        TaskRepository.create_activity(
            session=session,
            task_id=task_id,
            user_id=current_user.id,
            action=TaskActivityType.ASSIGNEE_REMOVED,
            field="assignee",
            old_value=str(assignee_id),
            new_value=None,
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
        task = TaskRepository.get_active_by_id(session, task_id)
        if task is None:
            raise TaskNotFoundError(
                "Task not found"
            )
            
        task_assignee = TaskRepository.get_by_task_user(session, task_id, user_id)
        
        if task_assignee is None:
            raise ForbiddenOperationError(
                "you are not an assignee for this task"
            )
            
        old_status = task_assignee.status
            
        updated_task_assignee = TaskRepository.update_assignee_status(
            session,
            task_assignee,
            update_status,
        )
        
        if old_status != updated_task_assignee.status:
            TaskRepository.create_activity(
                session=session,
                task_id=task_id,
                user_id=user_id,
                action=TaskActivityType.STATUS_CHANGED,
                field="status",
                old_value=old_status.value,
                new_value=updated_task_assignee.status.value,
            )
        
        return updated_task_assignee
        
        
        
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
        
        
    @staticmethod
    def get_deleted_tasks(
        session: Session,
        current_user: User,
        page: int = 1,
        limit: int = 10,
    ) -> TaskListResponse:

        is_admin = current_user.role == UserRole.ADMIN

        owner_id = None if is_admin else current_user.id

        tasks, total = TaskRepository.get_deleted_tasks(
            session,
            owner_id,
            page,
            limit,
        )

        task_responses = [task for task in tasks]

        total_pages = math.ceil(total / limit) if total > 0 else 0

        return TaskListResponse(
            tasks=task_responses,
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
        )
        
        
    @staticmethod
    def get_task_activities(
        session: Session,
        task_id: UUID,
        current_user: User,
        page: int = 1,
        limit: int = 10,
    ) -> TaskActivityListResponse:
        
        task = TaskRepository.get_by_id(session, task_id)
        
        if task is None:
            raise TaskNotFoundError(
                "Task not found"
            )
            
        is_owner = task.owner_id == current_user.id
        is_admin = current_user.role == UserRole.ADMIN

        if task.is_deleted:
            if not is_owner and not is_admin:
                raise ForbiddenOperationError(
                    "You don't have permission to see this task activities"
                )
        else:
            is_assignee = TaskRepository.get_by_task_user(
                session,
                task_id,
                current_user.id,
            ) is not None

            if not is_owner and not is_assignee and not is_admin:
                raise ForbiddenOperationError(
                    "You don't have permission to see this task activities"
                )
            
        activities, total = TaskRepository.get_task_activities(
            session,
            task_id,
            page,
            limit,
        )
        
        task_activities = [
            TaskActivityResponse(
                id = activity.id,
                action=activity.action,
                field=activity.field,
                old_value=activity.old_value,
                new_value=activity.new_value,
                user=ActivityUserResponse(
                    id=activity.user_id,
                    name=activity.user.name,
                    email=activity.user.email,
                ),
                created_at=activity.created_at,
            )
            for activity in activities
        ]
        
        
        total_pages = math.ceil(total / limit) if total > 0 else 0

        return TaskActivityListResponse(
            activities=task_activities,
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages
        )
        
        
            
       
            
            
        