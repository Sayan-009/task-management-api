class UserNotFoundError(Exception):
    pass

class TaskNotFoundError(Exception):
    pass


class ForbiddenOperationError(Exception):
    pass

class NoUpdateFieldsError(Exception):
    pass

class AlreadyAssignedError(Exception):
    pass


class DuplicateAssigneeError(Exception):
    pass

class UserInactiveError(Exception):
    pass


class AssignmentNotFoundError(Exception):
    pass


class TaskAlreadyDeletedError(Exception):
    pass

class TaskNotDeletedError(Exception):
    pass


class CommentNotFoundError(Exception):
    pass

class UpdateSameContentError(Exception):
    pass


class ConversationNotFoundError(Exception):
    pass

class MessageAlreadyDeletedError(Exception):
    pass

class MessageNotFoundError(Exception):
    pass

class MessageEditLimitExceededError(Exception):
    pass

class AttachmentNotFoundError(Exception):
    pass
class AttachmentNotAttachedError(Exception):
    pass
class AttachmentAlreadyAttachedError(Exception):
    pass