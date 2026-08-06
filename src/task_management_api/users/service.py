from task_management_api.users.schema import User, UserResponse


def user_register(user: User) -> UserResponse:
    
    return UserResponse(name=user.name, email=user.email)