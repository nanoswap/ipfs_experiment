import uuid
import ipfs
import utils

import nanoswap.message.identity_pb2 as identity_pb2
import nanoswap.message.lookup_pb2 as lookup_pb2
from models.return_types import NewCreditIdentity, NewLookup

def write_identity(id_content: str, id_type: int) -> NewCreditIdentity:
    # write identity
    identity = utils.new_identity(
        id_type,
        id_content
    )
    ipfs.write(identity.filename, identity.data)
    print(f"credit id created: {identity.credit_id}")
    return identity

def read_identity(filename: str) -> None:
    # read identity
    result = ipfs.read(filename, identity_pb2.Identity())
    print(f"read ssn: {result.id_field_content}")

def write_lookup(data: identity_pb2.Identity, credit_id: uuid.UUID) -> NewLookup:
    # write lookup
    lookup = utils.new_lookup(data, credit_id)
    ipfs.write(lookup.filename, lookup.data)
    return lookup

def read_lookup(filename: str) -> None:
    # read lookup
    response = ipfs.read(filename, lookup_pb2.Lookup())
    print(f"read credit id: {response.credit_identity}")
