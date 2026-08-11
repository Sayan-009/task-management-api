from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session


from task_management_api.db.session import get_db
from task_management_api.users.model import User
from task_management_api.users.repository import UserRepository
from task_management_api.core.token import TokenService

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/users/login",
)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_db),     
) -> User:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = TokenService.decode_access_token(token)
        
        subject = payload.get("sub")
        
        if subject is None:
            raise credentials_exception
        
        user_id = UUID(subject)
        
        
    except (ValueError, TypeError):
        raise credentials_exception from None
    
    user = UserRepository.get_by_id(
        session,
        user_id
    )
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
        
    return user