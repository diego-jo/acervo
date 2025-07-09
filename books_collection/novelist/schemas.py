from pydantic import BaseModel


class NovelistRequest(BaseModel):
    name: str


class NovelistResponse(NovelistRequest):
    id: int


class NovelistUpdate(BaseModel):
    name: str | None = None
