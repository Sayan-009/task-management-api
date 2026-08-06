from fastapi import APIRouter, status

from task_management_api.users.schema import (
    UserRegistraionRequest,
    MessageResponse
)

from task_management_api.users.service import register_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def register(request: UserRegistraionRequest):
    return register_user(request)