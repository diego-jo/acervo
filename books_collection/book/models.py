from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from books_collection.database.tables import table_registry
from books_collection.novelist.models import Novelist


@table_registry.mapped_as_dataclass
class Book:
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    year: Mapped[int]
    title: Mapped[str] = mapped_column(unique=True)
    novelist_id: Mapped[int] = mapped_column(ForeignKey('novelists.id'))

    novelist: Mapped['Novelist'] = relationship(
        init=False,
        back_populates='books',
        lazy='joined'
    )
