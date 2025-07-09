from pydantic import BaseModel, Field


class BookRequest(BaseModel):
    year: int = Field(max_length=4, min_length=4)
    title: str = Field(min_length=5)
    novelistId: int = Field(gt=0)


class BookResponse(BookRequest):
    id: int = Field(gt=0)


class BookUpdate(BaseModel):
    year: int = Field(max_length=4, min_length=4)
    title: str = Field(min_length=5)
    novelistId: int = Field(gt=0)
