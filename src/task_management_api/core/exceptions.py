class UserNotFoundError(Exception):
    pass


class TaskNotFoundError(Exception):
    pass


class ForbiddenOperationError(Exception):
    pass

class NoUpdateFieldsError(Exception):
    pass