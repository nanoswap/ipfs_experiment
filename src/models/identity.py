from __future__ import annotations
from dataclasses import dataclass
from uuid import UUID
from enum import Enum

import nanoswap.message.identity_pb2 as identity_pb2
import uuid
import ipfs

import nanoswap.message.identity_pb2 as identity_pb2

class CreditIdStatus(Enum):
    CREATED = 0
    RETRIEVED = 1

@dataclass
class CreditId:
    credit_identity: UUID
    filename: str
    status: CreditIdStatus

    def __init__(self, id_type: int, id_content: str):
        """
        For the given identity (id_value, id_type), either:
            1. retrieve the credit id corresponding to this identity
        or:
            2. create a new credit id for this identity
        
        Args:
            id_type (int): The kind of id
            id_content (str): The value of the id
        """
        self.filename = f"identity/{id_type}.{id_content}"

        # check if the identity already exists
        file_exists = ipfs.does_file_exist(self.filename)
        if not file_exists:

            # generate a new credit id
            self.credit_identity = uuid.uuid4()
            self.status = CreditIdStatus.CREATED

            # wrap it in a protobuf and write it to ipfs
            ipfs.add(self.filename, identity_pb2.Lookup(
                credit_identity = str(self.credit_id)
            ))
        
        else:

            # read the existing identity
            ipfs_data = ipfs.read(self.filename, identity_pb2.Lookup())
            self.credit_identity = uuid.UUID(ipfs_data.credit_identity)
            self.status = CreditIdStatus.RETRIEVED
