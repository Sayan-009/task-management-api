from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from task_management_api.users.model import User
from task_management_api.users.schema import UserStatusUpdate, UserRoleUpdate



class UserRepository:
    
    @staticmethod
    async def create(
        session: AsyncSession,
        user: User,
    ) -> User:
        session.add(user)
        await session.flush()
        
        return user
    
    @staticmethod
    async def get_by_email(
        session: AsyncSession,
        email: str,
    ) -> User | None:
        statement = select(User).where(User.email == email)
        
        result = await session.execute(statement)
        
        return result.scalar_one_or_none()
    
    
    @staticmethod
    async def get_by_id(
        session: AsyncSession,
        user_id: UUID,
    ) -> User | None:
        statement = select(User).where(User.id == user_id)
        
        result = await session.execute(statement)
        
        return result.scalar_one_or_none()
    
    
    @staticmethod
    async def update(
        session: AsyncSession,
        current_user: User,
        updates: dict,
    ) -> User:
        
        for field, value in updates.items():
            setattr(current_user, field, value)
            
        await session.flush()
        
        return current_user
    
    
    @staticmethod
    async def update_password(
        session: AsyncSession,
        current_user: User,
        new_password_hashed: str
    ) -> User:
        current_user.password_hash = new_password_hashed
        
        await session.flush()
        
        return current_user
    
    @staticmethod
    async def deactivate(
        session: AsyncSession,
        current_user: User
    ) -> None:
        current_user.is_active = False
        
        await session.flush()
        
        
    @staticmethod
    async def status_update(
        session: AsyncSession,
        user: User,
        user_status: UserStatusUpdate,
    ) -> None:
        user.is_active = user_status.is_active
        await session.flush()
        
        
    @staticmethod
    async def role_update(
        session: AsyncSession,
        user: User,
        role: UserRoleUpdate,
    ) -> None:
        user.role = role.role
        await session.flush()
                
    
    @staticmethod
    async def get_all(
        session: AsyncSession,
    ) -> list[User]:
        statement = select(User)

        result = await session.execute(statement)
        return result.scalars().all()
            
            