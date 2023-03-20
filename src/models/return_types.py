from dataclasses import dataclass
from uuid import UUID

import nanoswap.message.lookup_pb2 as lookup_pb2
from enum import Enum

class CreditIdStatus(Enum):
    CREATED = 0
    RETRIEVED = 1

@dataclass
class CreditId:
    id: UUID
    status: CreditIdStatus
