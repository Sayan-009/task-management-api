from pydantic import BaseModel, EmailStr, Field

class Base(BaseModel):
    name: str
    email: EmailStr
    
class User(Base):
    password: str = Field(min_length=8)
    
class UserResponse(Base):
    pass