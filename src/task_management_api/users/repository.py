from sqlalchemy import select
from sqlalchemy.orm import Session


from task_management_api.users.model import User

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