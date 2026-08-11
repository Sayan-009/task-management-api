from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session


from task_management_api.users.model import User
from task_management_api.users.schema import UserUpdate

class UserRepository:
    
    @staticmethod
    def create(
        session: Session,
        user: User,
    ) -> User:
        session.add(user)
        session.flush()
        
        return user
    
    @staticmethod
    def get_by_email(
        session: Session,
        email: str,
    ) -> User | None:
        statement = select(User).where(User.email == email)
        
        return session.execute(statement).scalar_one_or_none()
    
    
    @staticmethod
    def get_by_id(
        session: Session,
        user_id: UUID,
    ) -> User | None:
        statement = select(User).where(User.id == user_id)
        
        return session.execute(statement).scalar_one_or_none()
    
    
    @staticmethod
    def update(
        session: Session,
        current_user: User,
        updates: dict,
    ) -> User:
        
        for field, value in updates.items():
            setattr(current_user, field, value)
            
        session.flush()
        
        return current_user
    
    
    @staticmethod
    def update_password(
        session: Session,
        current_user: User,
        new_password_hashed: str
    ) -> User:
        current_user.password_hash = new_password_hashed
        
        session.flush()
        
        return current_user
    
    @staticmethod
    def deactivate(
        session: Session,
        current_user: User
    ) -> None:
        current_user.is_active = False
        
        session.flush()
        
       
            