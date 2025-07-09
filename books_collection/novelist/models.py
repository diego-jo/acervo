from sqlalchemy.orm import Mapped, mapped_column, relationship

from books_collection.book.models import Book
from books_collection.database.tables import table_registry


@table_registry.mapped_as_dataclass
class Novelist:
    __tablename__ = 'novelists'
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)

    books: Mapped[list['Book']] = relationship(
        init=False,
        cascade='all, delete-orphan',
        lazy='selectin',
        back_populates='novelist',
    )
