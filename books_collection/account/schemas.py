from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from books_collection.account.enums import State
from books_collection.common.filters import FilterPage

# TODO: validar erro de criação de model usando a regex abaixo
# error: look-around, including look-ahead and look-behind, is not supported
# 1# ref: https://stackoverflow.com/questions/61485063/is-there-alternative-regex-syntax-to-avoid-the-error-look-around-including-loo

# passwd_regex = r'^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*]).*$'


class AccountRequest(BaseModel):
    username: str = Field(min_length=5, max_length=15)
    email: EmailStr
    password: str = Field(min_length=10)


class AccountResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    state: State

    model_config = ConfigDict(from_attributes=True)


class AccountUpdate(BaseModel):
    username: Optional[str] = Field(default=None)
    email: Optional[EmailStr] = Field(default=None)
    password: Optional[str] = Field(min_length=10, default=None)
    state: Optional[State] = Field(default=None)


class AccountsList(BaseModel):
    accounts: list[AccountResponse]


class FilterAccount(FilterPage):
    state: Optional[State] = Field(default=None)
