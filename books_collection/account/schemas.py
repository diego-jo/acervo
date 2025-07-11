from typing import Optional

from pydantic import BaseModel, EmailStr, Field

passwd_regex = r'^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*]).*$'


class AccountRequest(BaseModel):
    username: str = Field(min_length=5, max_length=15)
    email: EmailStr
    password: str = Field(min_length=10, pattern=passwd_regex)


class AccountResponse(BaseModel):
    id: int
    username: str
    email: EmailStr


class AccountUpdate(BaseModel):
    username: Optional[str] = Field(default=None)
    email: Optional[EmailStr] = Field(default=None)
    password: Optional[str] = Field(min_length=10, pattern=passwd_regex)
