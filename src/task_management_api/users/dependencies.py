from fastapi import Depends, HTTPException, status


from task_management_api.users.model import User
from task_management_api.core.dependencies import get_current_user

from task_management_api.users.enums import UserRole


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:

    if current_user.role == UserRole.ADMIN:
        return current_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User is not an admin",
    )
    