from pydantic import BaseModel, EmailStr
from typing import Optional

class RegisterIn(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_admin: Optional[bool] = False

    class Config:
        from_attributes = True  # SQLAlchemy objesinden dönüşe izin

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
