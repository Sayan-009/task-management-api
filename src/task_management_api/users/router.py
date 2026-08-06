from fastapi import APIRouter, status

from task_management_api.users.schema import User, UserResponse
from task_management_api.users.service import user_register

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: User) -> UserResponse:
    return user_register(user)
