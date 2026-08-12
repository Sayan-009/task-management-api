from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from task_management_api.users.enums import UserRole

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128) 
    
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    
    
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    
    
    
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
    
class UserUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )
    email: EmailStr | None = None
    
    
class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
    
    
class MessageResponse(BaseModel):
    message: str


class UserStatusUpdate(BaseModel):
    is_active: bool