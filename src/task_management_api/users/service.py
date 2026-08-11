from sqlalchemy.orm import Session

from task_management_api.core.security import hash_password, verify_password
from task_management_api.users.model import User
from task_management_api.users.repository import UserRepository
from task_management_api.users.schema import UserUpdate


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
    
    
    @staticmethod
    def update_user(
        session: Session,
        current_user: User,
        update_data: UserUpdate
    ) -> User:
        updates = update_data.model_dump(exclude_unset=True)
        if not updates:
            raise ValueError("No fields provided for update")
        
        if "email" in updates:
            new_email = updates["email"]

            if new_email != current_user.email:
                existing_user = UserRepository.get_by_email(
                    session,
                    new_email,
                )

                if existing_user is not None:
                    raise ValueError(
                        "Email already exists, use a different email"
                    )
        
        return UserRepository.update(
            session,
            current_user,
            updates,
        )
        
        
    @staticmethod
    def update_password(
        session: Session,
        current_user: User,
        current_password: str,
        new_password: str
    ) -> User:
        if not verify_password(
            current_password,
            current_user.password_hash   
        ):
            raise ValueError("Current password is incorrect")
        
        if current_password == new_password:
            raise ValueError("new password must be differnt from current password")
        
        
        new_password_hashed = hash_password(new_password)
        
        return UserRepository.update_password(
            session,
            current_user,
            new_password_hashed
        )
        
        
    @staticmethod
    def deactivate_user(
        session: Session,
        current_user: User
    ) -> None:
        UserRepository.deactivate(
            session,
            current_user
        )
       
                
        
                
        
        