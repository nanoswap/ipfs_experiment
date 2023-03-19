from dataclasses import dataclass
from uuid import UUID

import nanoswap.message.identity_pb2 as identity_pb2
import nanoswap.message.lookup_pb2 as lookup_pb2

@dataclass
class NewCreditIdentity:
    credit_id: UUID
    filename: str
    data: identity_pb2.Identity

@dataclass
class NewLookup:
    filename: str
    data: lookup_pb2.Lookup
