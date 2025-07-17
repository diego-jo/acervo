from pydantic import BaseModel, Field


class FilterPage(BaseModel):
    # TODO: validar números positivos
    offset: int = Field(default=0)
    limit: int = Field(default=20)
