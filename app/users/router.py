from fastapi import APIRouter, status

from app.users.schema import User, UserResponse
from app.users.service import user_register

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: User) -> UserResponse:
    return user_register(user)