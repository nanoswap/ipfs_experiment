from dataclasses import dataclass
from uuid import UUID

import nanoswap.message.identity_pb2 as identity_pb2

@dataclass
class NewCreditIdentity:
    credit_id: UUID
    filename: str
    data: identity_pb2.Identity
