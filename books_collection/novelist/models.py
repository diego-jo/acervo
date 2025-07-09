from __future__ import annotations

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from books_collection.database.tables import table_registry


@table_registry.mapped_as_dataclass
class Novelist:
    __tablename__ = 'novelists'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)

    books: Mapped[list['Book']] = relationship(  # noqa: F821 # type: ignore
        init=False,
        cascade='all, delete-orphan',
        lazy='selectin',
        back_populates='novelist',
    )

    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
