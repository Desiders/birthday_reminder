from dataclasses import dataclass
from uuid import UUID


@dataclass
class User:
    id: UUID
    tg_id: int


@dataclass
class UsersStats:
    count: int
    new_users_per_day: int
    new_users_per_week: int
    new_users_per_month: int
