from uuid import UUID
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from task_management_api.db.session import get_db
from task_management_api.users.model import User
from task_management_api.users.schema import (
    UserCreate, 
    UserResponse,
    UserLogin,
    TokenResponse,
    UserUpdate,
    ChangePasswordRequest,
    MessageResponse,
    UserStatusUpdate,
    UserRoleUpdate
)
from task_management_api.users.service import UserService
from task_management_api.core.token import TokenService
from task_management_api.core.dependencies import get_current_user
from task_management_api.users.dependencies import require_admin


router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_db),
) -> UserResponse:
    try:
        user = await UserService.create_user(
            session=session,
            name=user_data.name,
            email=user_data.email,
            password=user_data.password
        )
        
        await session.commit()
        
        return user
    
    except Exception:
        await session.rollback()
        raise
        
        

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login_user(
    user_data: UserLogin,
    session: AsyncSession = Depends(get_db),
) -> TokenResponse:
    user = await UserService.login_user(
        session=session,
        email=user_data.email,
        password=user_data.password,
    )

    access_token = TokenService.create_access_token(
        subject=str(user.id)
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


@router.post("/token", response_model=TokenResponse)
async def login_for_swagger(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db),
) -> TokenResponse:
    user = await UserService.login_user(
        session=session,
        email=form_data.username,
        password=form_data.password,
    )

    access_token = TokenService.create_access_token(
        subject=str(user.id)
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )



@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    return current_user


@router.patch("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def current_user_update(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> UserResponse:
    try:
        updated_user = await UserService.update_user(
            session,
            current_user,
            update_data
        )
        
        await session.commit()
        
        return updated_user
    
    except Exception:
        await session.rollback()
        raise
        
        
        
@router.patch("/me/password", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def password_update(
    passwords: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
) -> MessageResponse:
    try:
        await UserService.update_password(
            session,
            current_user,
            current_password=passwords.current_password,
            new_password=passwords.new_password,
        )
        
        await session.commit()
        
        return MessageResponse(message="Password changed successfully")
    
    except Exception:
        await session.rollback()
        raise
        
        

@router.patch("/me/deactivate", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def user_deactivate(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> MessageResponse:
    try:
        
        await UserService.deactivate_user(session, current_user)
        
        await session.commit()
                
        return MessageResponse(message="User deactivated successfully")

    except Exception:
        await session.rollback()
        raise


@router.get(
    "/",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
)
async def all_users(
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> list[UserResponse]:
    return await UserService.get_all_users(session)


@router.patch("/{user_id}/status", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def update_user_status(
    user_id: UUID,
    user_status: UserStatusUpdate,
    admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db)
) -> MessageResponse:
    
    try:
        await UserService.user_status_update(admin, session, user_id, user_status)
        
        await session.commit()
        
        return MessageResponse(message="User status updated successfully")
    
    except Exception:
        await session.rollback()
        raise
        
        
@router.patch("/{user_id}/role", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def update_user_role(
    user_id: UUID,
    role: UserRoleUpdate,
    admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db)
) -> MessageResponse:
    
    try:
        await UserService.user_role_update(admin, session, user_id, role)
        
        await session.commit()
        
        return MessageResponse(message="User role updated successfully")
    
    except Exception:
        await session.rollback()
        raise 