from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    
    
class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    
    
class TaskOrder(str, Enum):
    ASC = 'asc'
    DESC = "decs"
    
class TaskSort(str, Enum):
    TITLE = "title"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    STATUS = "status"
    PRIORITY = "priority"
    
    
class AssignedTaskSort(str, Enum):
    TITLE = "title"
    STATUS = "status"
    PRIORITY = "priority"
    

class TaskActivityType(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    STATUS_CHANGED = "status_changed"
    PRIORITY_CHANGED = "priority_changed"
    ASSIGNEE_ADDED = "assignee_added"
    ASSIGNEE_REMOVED = "assignee_removed"
    DELETED = "deleted"
    RESTORED = "restored"
    
    