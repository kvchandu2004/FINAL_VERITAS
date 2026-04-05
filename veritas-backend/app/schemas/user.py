from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str  # 'author' or 'editor'
    affiliation: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    affiliation: Optional[str]
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str