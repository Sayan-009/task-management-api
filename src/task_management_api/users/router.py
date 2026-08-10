from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from task_management_api.db.session import get_db
from task_management_api.users.schema import UserCreate, UserResponse
from task_management_api.users.service import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    session: Session = Depends(get_db),
) -> UserResponse:
    try:
        user = UserService.create_user(
            session=session,
            name=user_data.name,
            email=user_data.email,
            password=user_data.password
        )
        
        session.commit()
        
        return user
    
    except ValueError as exc:
        session.rollback()
        
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
