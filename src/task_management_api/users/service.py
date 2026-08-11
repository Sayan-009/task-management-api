from sqlalchemy.orm import Session

from task_management_api.core.security import hash_password, verify_password
from task_management_api.users.model import User
from task_management_api.users.repository import UserRepository


class UserService:
    
    @staticmethod
    def create_user(
        session: Session,
        name: str,
        email: str,
        password: str,
    ) -> User:
        existing_user = UserRepository.get_by_email(
            session,
            email,
        )
        
        if existing_user is not None:
            raise ValueError("User with this email already exists")
        
        
        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password)
        )
        
        return UserRepository.create(
            session,
            user,
        )
        
    
    @staticmethod 
    def login_user(
        session: Session,
        email: str,
        password: str 
    ) -> User:
        exising_user = UserRepository.get_by_email(
            session,
            email,
        )
        
        if exising_user is None:
            raise ValueError(
                "Invalid email or password"
            )
        
        if not verify_password(
            password,
            exising_user.password_hash
        ):
            raise ValueError("Invalid email or password")
         
        
        if not exising_user.is_active:
            raise ValueError("User account is inactive")

        return exising_user
        
        