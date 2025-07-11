from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    expires_in: int
    token_type: str = Field(default='Bearer')
