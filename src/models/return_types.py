from dataclasses import dataclass
from uuid import UUID

from enum import Enum


class CreditIdStatus(Enum):
    CREATED = 0
    RETRIEVED = 1

@dataclass
class CreditId:
    id: UUID
    status: CreditIdStatus
