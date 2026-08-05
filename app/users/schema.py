from pydantic import BaseModel, EmailStr, Field

class Base(BaseModel):
    pass
    
class User(Base):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)
    

class Message(Base):
    message: str