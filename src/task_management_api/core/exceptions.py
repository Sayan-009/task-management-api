from fastapi import status


class AppException(Exception):

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    code = "INTERNAL_ERROR"

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
        
# Credentials
class InvalidCredentialsError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "INVALID_CREDENTIALS"
    
class PasswordUnchangedError(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "PASSWORD_UNCHANGED"

# Users
class UserAlreadyExistsError(AppException):
    status_code = status.HTTP_409_CONFLICT
    code = "USER_ALREADY_EXISTS"
    
class UserNotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    code = "USER_NOT_FOUND"


class UserInactiveError(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    code = "USER_INACTIVE"
    
class CannotModifyOwnAccountError(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    code = "CANNOT_MODIFY_OWN_ACCOUNT"


# Tasks
class TaskNotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    code = "TASK_NOT_FOUND"


class ForbiddenOperationError(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    code = "FORBIDDEN_OPERATION"


class NoUpdateFieldsError(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "NO_UPDATE_FIELDS"


class TaskAlreadyDeletedError(AppException):
    status_code = status.HTTP_409_CONFLICT
    code = "TASK_ALREADY_DELETED"


class TaskNotDeletedError(AppException):
    status_code = status.HTTP_409_CONFLICT
    code = "TASK_NOT_DELETED"


# Task assignments
class AlreadyAssignedError(AppException):
    status_code = status.HTTP_409_CONFLICT
    code = "ALREADY_ASSIGNED"


class DuplicateAssigneeError(AppException):
    status_code = status.HTTP_409_CONFLICT
    code = "DUPLICATE_ASSIGNEE"


class AssignmentNotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    code = "ASSIGNMENT_NOT_FOUND"


# Comments
class CommentNotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    code = "COMMENT_NOT_FOUND"


class UpdateSameContentError(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "UPDATE_SAME_CONTENT"


# Conversations
class ConversationNotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    code = "CONVERSATION_NOT_FOUND"


# Messages
class MessageNotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    code = "MESSAGE_NOT_FOUND"


class MessageAlreadyDeletedError(AppException):
    status_code = status.HTTP_409_CONFLICT
    code = "MESSAGE_ALREADY_DELETED"


class MessageEditLimitExceededError(AppException):
    status_code = status.HTTP_409_CONFLICT
    code = "MESSAGE_EDIT_LIMIT_EXCEEDED"
    
class MessageContentUnchangedError(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "MESSAGE_CONTENT_UNCHANGED"


# Attachments

class InvalidAttachmentError(AppException):
    status_code = 400
    code = "INVALID_ATTACHMENT"
    
class AttachmentNotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    code = "ATTACHMENT_NOT_FOUND"


class AttachmentNotAttachedError(AppException):
    status_code = status.HTTP_409_CONFLICT
    code = "ATTACHMENT_NOT_ATTACHED"


class AttachmentAlreadyAttachedError(AppException):
    status_code = status.HTTP_409_CONFLICT
    code = "ATTACHMENT_ALREADY_ATTACHED"
