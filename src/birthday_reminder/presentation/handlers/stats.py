from logging import getLogger

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from birthday_reminder.application.birthday_remind import BirthdayRemindReader
from birthday_reminder.application.birthday_remind.queries import (
    GetBirthdayRemindersStats,
)
from birthday_reminder.application.common import UnitOfWork
from birthday_reminder.application.user import UserReader
from birthday_reminder.application.user.queries import GetUsersStats
from birthday_reminder.presentation.i18n import FormatText

logger = getLogger(__name__)

router = Router(name="stats_router")


@router.message(Command("stats"))
async def stats(
    message: Message,
    uow: UnitOfWork,
    user_reader: UserReader,
    birthday_remind_reader: BirthdayRemindReader,
    format_text: FormatText,
) -> None:
    users_stats_query = GetUsersStats(user_reader, uow)
    birthday_reminders_stats_query = GetBirthdayRemindersStats(
        birthday_remind_reader, uow
    )

    users_stats = await users_stats_query()
    birthday_reminders_stats = await birthday_reminders_stats_query()

    text = format_text(
        "stats",
        {
            "total_users": users_stats.count,
            "new_users_today": users_stats.new_users_per_day,
            "new_users_week": users_stats.new_users_per_week,
            "new_users_month": users_stats.new_users_per_month,
            "total_reminders": birthday_reminders_stats.count,
            "new_reminders_today": birthday_reminders_stats.new_birthday_remiders_per_day,
            "new_reminders_week": birthday_reminders_stats.new_birthday_remiders_per_week,
            "new_reminders_month": birthday_reminders_stats.new_birthday_remiders_per_month,
            "avg_reminders_per_user": birthday_reminders_stats.count
            / users_stats.count,
        },
    )

    await message.answer(
        text,
        parse_mode=None,
        disable_web_page_preview=True,
        disable_notification=False,
    )
