from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7

from birthday_reminder.domain.completed_birthday_remind.entities import (
    ReminderType,
)

from .base import TimedBaseModel


class CompletedBirthdayRemind(TimedBaseModel):
    __tablename__ = "completed_birthday_reminds"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid7,
        server_default=sa.func.uuid_generate_v7(),
    )
    birthday_remind_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey("birthday_reminds.id"), nullable=False
    )
    year: Mapped[int] = mapped_column(nullable=False)
    reminder_type: Mapped[ReminderType] = mapped_column(nullable=False)

    UniqueConstraint(birthday_remind_id, year, reminder_type)
