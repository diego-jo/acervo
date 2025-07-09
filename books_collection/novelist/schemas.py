from typing import Optional

from pydantic import BaseModel, Field


class NovelistRequest(BaseModel):
    name: str


class NovelistResponse(NovelistRequest):
    id: int


class NovelistUpdate(BaseModel):
    name: Optional[str] = Field(default=None)
