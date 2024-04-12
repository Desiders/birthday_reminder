from birthday_reminder.domain.birthday_remind.entities import BirthdayRemind
from birthday_reminder.domain.completed_birthday_remind.entities import (
    CompletedBirthdayRemind,
)
from birthday_reminder.domain.user.entities import User

from . import models


def model_to_user(user: models.User) -> User:
    return User(
        id=user.id,
        language_code=user.language_code,
        tg_id=user.tg_id,
    )


def user_to_model(user: User) -> models.User:
    return models.User(
        id=user.id,
        language_code=user.language_code,
        tg_id=user.tg_id,
    )


def model_to_birthday_remind(
    birthday_remind: models.BirthdayRemind,
) -> BirthdayRemind:
    return BirthdayRemind(
        id=birthday_remind.id,
        user_id=birthday_remind.user_id,
        name=birthday_remind.name,
        day=birthday_remind.day,
        month=birthday_remind.month,
    )


def birthday_remind_to_model(
    birthday_remind: BirthdayRemind,
) -> models.BirthdayRemind:
    return models.BirthdayRemind(
        id=birthday_remind.id,
        user_id=birthday_remind.user_id,
        name=birthday_remind.name,
        day=birthday_remind.day,
        month=birthday_remind.month,
    )


def completed_birthday_remind_to_model(
    completed_birthday_remind: CompletedBirthdayRemind,
) -> models.CompletedBirthdayRemind:
    return models.CompletedBirthdayRemind(
        id=completed_birthday_remind.id,
        birthday_remind_id=completed_birthday_remind.birthday_remind_id,
        year=completed_birthday_remind.year,
        reminder_type=completed_birthday_remind.reminder_type,
    )


def model_to_completed_birthday_remind(
    completed_birthday_remind: models.CompletedBirthdayRemind,
) -> CompletedBirthdayRemind:
    return CompletedBirthdayRemind(
        id=completed_birthday_remind.id,
        birthday_remind_id=completed_birthday_remind.birthday_remind_id,
        year=completed_birthday_remind.year,
        reminder_type=completed_birthday_remind.reminder_type,
    )
