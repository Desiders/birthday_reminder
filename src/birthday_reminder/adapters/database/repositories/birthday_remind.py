from datetime import timedelta
from uuid import UUID

from sqlalchemy import case, delete, func, select

from birthday_reminder.adapters.database.converters import (
    birthday_remind_to_model,
    model_to_birthday_remind,
)
from birthday_reminder.application.birthday_remind import (
    BirthdayRemindReader,
    BirthdayRemindRepo,
)
from birthday_reminder.domain.birthday_remind.entities import (
    BirthdayRemind,
    BirthdayRemindersStats,
)
from birthday_reminder.domain.birthday_remind.exceptions import IDNotFound

from ..exception_mapper import exception_mapper
from ..models import BirthdayRemind as BirthdayRemindModel
from .base import Repo


class BirthdayRemindRepoImpl(Repo, BirthdayRemindRepo):
    @exception_mapper
    async def add(self, birthday_remind: BirthdayRemind) -> None:
        self._session.add(birthday_remind_to_model(birthday_remind))

        await self._session.flush()

    @exception_mapper
    async def delete_by_id(self, id: UUID) -> None:
        await self._session.execute(
            delete(BirthdayRemindModel).filter(BirthdayRemindModel.id == id)
        )


class BirthdayRemindReaderImpl(Repo, BirthdayRemindReader):
    @exception_mapper
    async def get_by_id(self, id: UUID) -> BirthdayRemind:
        birthday_remind = await self._session.scalar(
            select(BirthdayRemindModel).filter(BirthdayRemindModel.id == id)
        )

        if birthday_remind is None:
            raise IDNotFound(id)

        return model_to_birthday_remind(birthday_remind)

    @exception_mapper
    async def get_by_user_id(self, user_id: UUID) -> list[BirthdayRemind]:
        birthday_reminds = await self._session.scalars(
            select(BirthdayRemindModel).filter(
                BirthdayRemindModel.user_id == user_id
            )
        )

        return [
            model_to_birthday_remind(birthday_remind)
            for birthday_remind in birthday_reminds
        ]

    @exception_mapper
    async def get_by_user_id_and_sort_by_nearest(
        self, user_id: UUID, now_day: int, now_month: int
    ) -> list[BirthdayRemind]:
        birthday_reminds = await self._session.scalars(
            select(BirthdayRemindModel)
            .filter(BirthdayRemindModel.user_id == user_id)
            .order_by(
                # Sort by the difference between the current month and the month of the birthday in ascending order.
                # If the month of the birthday has already passed this year, it will be in the end,
                # and if the month of the birthday has not yet passed this year, it will be in the start
                # where the first place will be the birthday that is closest to the current month.
                case(
                    # If the month of the birthday has already passed this year,
                    # we need to calculate the difference between the current month
                    # and the month of the birthday next year.
                    (
                        (BirthdayRemindModel.month - now_month) < 0,
                        12 + (BirthdayRemindModel.month - now_month),
                    ),
                    # If the month of the birthday is the current month
                    # and the day of the birthday has already passed this month,
                    # so we need to pass `12` to the `case` function to sort it in the end.
                    (
                        ((BirthdayRemindModel.month - now_month) == 0)
                        & (BirthdayRemindModel.day - now_day < 0),
                        12,
                    ),
                    # If the month of the birthday has not yet passed this year,
                    # we need to calculate the difference between the current month
                    # and the month of the birthday this year.
                    else_=BirthdayRemindModel.month - now_month,
                ).asc(),
                # Sort by the difference between the current day and the day of the birthday in ascending order.
                # Cases when the month of the birthday is the current month and the day of the birthday has already passed this month
                # are already sorted by the previous case,
                # so we just sort by the difference between the current day and the day of the birthday.
                (BirthdayRemindModel.day - now_day).asc(),
            )
        )

        return [
            model_to_birthday_remind(birthday_remind)
            for birthday_remind in birthday_reminds
        ]

    @exception_mapper
    async def get_birthday_reminders_stats(self) -> BirthdayRemindersStats:
        result = await self._session.execute(
            select(
                func.count(BirthdayRemindModel.id),
                func.count().filter(
                    BirthdayRemindModel.created_at
                    > func.now() - timedelta(days=1)
                ),
                func.count().filter(
                    BirthdayRemindModel.created_at
                    > func.now() - timedelta(weeks=1)
                ),
                func.count().filter(
                    BirthdayRemindModel.created_at
                    > func.now() - timedelta(days=30)
                ),
            )
        )

        return BirthdayRemindersStats(*result.one())
