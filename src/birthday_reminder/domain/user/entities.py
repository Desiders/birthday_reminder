from dataclasses import dataclass
from uuid import UUID


@dataclass
class User:
    id: UUID
    tg_id: int
