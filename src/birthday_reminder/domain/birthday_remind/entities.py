from dataclasses import dataclass
from uuid import UUID


@dataclass
class BirthdayRemind:
    id: UUID
    user_id: UUID
    name: str
    day: int
    month: int
