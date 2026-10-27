from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from task_management_api.core.security import hash_password, verify_password
from task_management_api.users.model import User
from task_management_api.users.repository import UserRepository
from task_management_api.users.schema import UserUpdate, UserStatusUpdate, UserRoleUpdate
from task_management_api.core.exceptions import (
    UserNotFoundError,
    UserInactiveError,
    NoUpdateFieldsError,
    CannotModifyOwnAccountError,
    PasswordUnchangedError,
    UserAlreadyExistsError,
    InvalidCredentialsError,
)



class UserService:
    
    @staticmethod
    async def create_user(
        session: AsyncSession,
        name: str,
        email: str,
        password: str,
    ) -> User:
        existing_user = await UserRepository.get_by_email(
            session,
            email,
        )
        
        if existing_user is not None:
            raise UserAlreadyExistsError("User with this email already exists")
        
        
        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password)
        )
        
        return await UserRepository.create(
            session,
            user,
        )
        
    
    @staticmethod 
    async def login_user(
        session: AsyncSession,
        email: str,
        password: str 
    ) -> User:
        existing_user = await UserRepository.get_by_email(
            session,
            email,
        )
        
        if existing_user is None:
            raise InvalidCredentialsError("Invalid email or password")
        
        if not verify_password(
            password,
            existing_user.password_hash
        ):
            raise InvalidCredentialsError("Invalid email or password")
         
        
        if not existing_user.is_active:
            raise UserInactiveError("User account is inactive")

        return existing_user
    
    
    @staticmethod
    async def update_user(
        session: AsyncSession,
        current_user: User,
        update_data: UserUpdate
    ) -> User:
        updates = update_data.model_dump(exclude_unset=True)
        if not updates:
            raise NoUpdateFieldsError("No fields provided for update")
        
        if "email" in updates:
            new_email = updates["email"]

            if new_email != current_user.email:
                existing_user = await UserRepository.get_by_email(
                    session,
                    new_email,
                )

                if existing_user is not None:
                    raise UserAlreadyExistsError("User with this email already exists")
        
        return await UserRepository.update(
            session,
            current_user,
            updates,
        )
        
        
    @staticmethod
    async def update_password(
        session: AsyncSession,
        current_user: User,
        current_password: str,
        new_password: str
    ) -> User:
        if not verify_password(
            current_password,
            current_user.password_hash   
        ):
            raise InvalidCredentialsError("Current password is incorrect")
        
        if current_password == new_password:
            raise PasswordUnchangedError("New password must be different from current password")
        
        
        new_password_hashed = hash_password(new_password)
        
        return await UserRepository.update_password(
            session,
            current_user,
            new_password_hashed
        )
        
        
    @staticmethod
    async def deactivate_user(
        session: AsyncSession,
        current_user: User
    ) -> None:
        await UserRepository.deactivate(
            session,
            current_user
        )
       
       
    @staticmethod
    async def get_all_users(
        session: AsyncSession,
    ) -> list[User]:
        return await UserRepository.get_all(session)
    
    
    @staticmethod
    async def user_status_update(
        admin: User,
        session: AsyncSession,
        user_id: UUID,
        user_status: UserStatusUpdate,
    ) -> None:
        
        target_user = await UserRepository.get_by_id(
            session,
            user_id,
        )

        if target_user is None:
            raise UserNotFoundError("User not found")

        if admin.id == user_id:
            raise CannotModifyOwnAccountError("Admin can't change own status")

        await UserRepository.status_update(
            session,
            target_user,
            user_status,
        )
        
        
        
    @staticmethod
    async def user_role_update(
        admin: User,
        session: AsyncSession,
        user_id: UUID,
        role: UserRoleUpdate,
    ) -> None:
        
        target_user = await UserRepository.get_by_id(
            session,
            user_id,
        )

        if target_user is None:
            raise UserNotFoundError("User not found")

        if admin.id == user_id:
            raise CannotModifyOwnAccountError("Admin can't change own role")

        await UserRepository.role_update(
            session,
            target_user,
            role,
        )       
        
                    
        
                
        
        