from dataclasses import dataclass
from enum import Enum
from uuid import UUID


class ReminderType(Enum):
    BeforehandInOneDay = "BeforehandInOneDay"
    OnTheDay = "OnTheDay"


@dataclass
class CompletedBirthdayRemind:
    id: UUID
    birthday_remind_id: UUID
    year: int
    reminder_type: ReminderType
