from dataclasses import dataclass
from uuid import UUID


@dataclass
class BirthdayRemind:
    id: UUID
    user_id: UUID
    name: str
    day: int
    month: int


@dataclass
class BirthdayRemindersStats:
    count: int
    new_birthday_remiders_per_day: int
    new_birthday_remiders_per_week: int
    new_birthday_remiders_per_month: int
