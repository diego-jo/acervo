from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from books_collection.account.enums import State
from books_collection.database.tables import table_registry


@table_registry.mapped_as_dataclass
class Account:
    __tablename__ = 'accounts'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    state: Mapped[State] = mapped_column(
        default=State.enabled,
        server_default=State.enabled.value,
    )

    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
