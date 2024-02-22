from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7

from .base import TimedBaseModel


class BirthdayRemind(TimedBaseModel):
    __tablename__ = "birthday_reminds"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid7,
        server_default=sa.func.uuid_generate_v7(),
    )
    user_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey("users.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(nullable=False)
    day: Mapped[int] = mapped_column(nullable=False)
    month: Mapped[int] = mapped_column(nullable=False)
