from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from task_management_api.db.session import get_db
from task_management_api.users.model import User
from task_management_api.users.schema import (
    UserCreate, 
    UserResponse,
    UserLogin,
    TokenResponse,
)
from task_management_api.users.service import UserService
from task_management_api.core.token import TokenService
from task_management_api.core.dependencies import get_current_user

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
        
        

@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login_user(
    user_data: UserLogin,
    session: Session = Depends(get_db)
) -> TokenResponse:
    try:
        user = UserService.login_user(
            session=session,
            email=user_data.email,
            password=user_data.password,
        )
        
        access_token = TokenService.create_access_token(subject=str(user.id))
        
        return TokenResponse(
            token=access_token,
            token_type="bearer",
        )
        
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    return current_user