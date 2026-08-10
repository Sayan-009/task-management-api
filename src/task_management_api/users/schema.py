from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict

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
    is_active: bool
    
    
class TokenResponse(BaseModel):
    token: str
    token_type: str = "bearer"

