from pydantic import BaseModel, EmailStr, Field

class Base(BaseModel):
    pass
    
class UserRegistraionRequest(Base):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)
    

class MessageResponse(Base):
    message: str