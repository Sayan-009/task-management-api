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

class UserNotFoundError(Exception):
    pass

class UserInactiveError(Exception):
    pass


class AssignmentNotFoundError(Exception):
    pass


class TaskAlreadyDeletedError(Exception):
    pass

class TaskNotDeletedError(Exception):
    pass