from typing import Optional

from pydantic import BaseModel, Field

from books_collection.common.filters import FilterPage


class NovelistRequest(BaseModel):
    name: str


class NovelistResponse(NovelistRequest):
    id: int


class NovelistUpdate(BaseModel):
    name: Optional[str] = Field(default=None)


class NovelistList(BaseModel):
    novelists: list[NovelistResponse]


class FilterNovelist(FilterPage):
    name: Optional[str] = Field(default=None)
