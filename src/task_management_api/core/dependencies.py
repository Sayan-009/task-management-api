from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session


from task_management_api.db.session import get_db
from task_management_api.users.model import User
from task_management_api.users.repository import UserRepository
from task_management_api.core.token import TokenService
from task_management_api.core.exceptions import (
    UserInactiveError,
    InvalidCredentialsError,
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/users/token",
)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_db),     
) -> User:
    
    try:
        payload = TokenService.decode_access_token(token)
        
        subject = payload.get("sub")
        
        if subject is None:
            raise InvalidCredentialsError(
                "Could not validate credentials."
            )
        
        user_id = UUID(subject)
        
        
    except (ValueError, TypeError):
        raise InvalidCredentialsError(
            "Could not validate credentials."
        ) from None
    
    user = UserRepository.get_by_id(
        session,
        user_id
    )
    
    if user is None:
        raise InvalidCredentialsError(
            "Could not validate credentials."
        )
    
    if not user.is_active:
        raise UserInactiveError("User account is inactive")
        
        
    return user