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

logger = getLogger(__name__)

router = Router(name="stats_router")


@router.message(Command("stats"))
async def stats(
    message: Message,
    uow: UnitOfWork,
    user_reader: UserReader,
    birthday_remind_reader: BirthdayRemindReader,
) -> None:
    users_stats_query = GetUsersStats(user_reader, uow)
    birthday_reminders_stats_query = GetBirthdayRemindersStats(
        birthday_remind_reader, uow
    )

    users_stats = await users_stats_query()
    birthday_reminders_stats = await birthday_reminders_stats_query()

    text = (
        "Users stats:\n\n"
        f"Total users: {users_stats.count}\n"
        f"New users today: {users_stats.new_users_per_day}\n"
        f"New users this week: {users_stats.new_users_per_week}\n"
        f"New users this month: {users_stats.new_users_per_month}\n\n"
        "Birthday reminders stats:\n\n"
        f"Total birthday reminders: {birthday_reminders_stats.count}\n"
        f"New birthday reminders today: {birthday_reminders_stats.new_birthday_remiders_per_day}\n"
        f"New birthday reminders this week: {birthday_reminders_stats.new_birthday_remiders_per_week}\n"
        f"New birthday reminders this month: {birthday_reminders_stats.new_birthday_remiders_per_month}\n"
        f"Average birthday reminders per user: {birthday_reminders_stats.count / users_stats.count}\n"
    )

    await message.answer(
        text,
        parse_mode=None,
        disable_web_page_preview=True,
        disable_notification=False,
    )
