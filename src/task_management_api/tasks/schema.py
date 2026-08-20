from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, EmailStr

from task_management_api.tasks.enums import TaskPriority, TaskStatus, TaskActivityType


class TaskCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
    )
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
    )
    
class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    description: str | None = None
    priority: TaskPriority
    status: TaskStatus 
    created_at: datetime
    updated_at: datetime
    
    
class TaskOwnerResponse(BaseModel):
    id: UUID
    name: str
    status: TaskStatus


class TaskParticipantResponse(BaseModel):
    user_id: UUID
    name: str
    status: TaskStatus


class TaskDetailResponse(BaseModel):
    id: UUID
    title: str
    description: str | None = None
    priority: TaskPriority
    status: TaskStatus

    owner: TaskOwnerResponse
    assignees: list[TaskParticipantResponse]
    
    
class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    page: int
    limit: int
    total: int
    total_pages: int
    
    
class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length = 1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    priority: TaskPriority | None = None
    
class TaskStatusUpdate(BaseModel):
    status: TaskStatus
    

class TaskAssigneeCreate(BaseModel):
    assignee_ids: list[UUID] = Field(min_length=1)
    
    
class TaskAssigneeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    task_id: UUID
    status: TaskStatus
    created_at: datetime
    
    
class AssignedTaskResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    priority: TaskPriority
    my_status: TaskStatus
    owner: TaskOwnerResponse
    
    
class AssignedTaskListResponse(BaseModel):
    assigned_tasks: list[AssignedTaskResponse]
    page: int
    limit: int
    total: int
    total_pages: int
    
    
class ActivityUserResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr


class TaskActivityResponse(BaseModel):
    id: UUID
    action: TaskActivityType
    field: str | None = None
    old_value: str | None = None
    new_value: str | None = None
    user: ActivityUserResponse
    created_at: datetime


class TaskActivityListResponse(BaseModel):
    activities: list[TaskActivityResponse]
    page: int
    limit: int
    total: int
    total_pages: int
    
    


    
    