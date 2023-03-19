
import ipfs
import utils

import nanoswap.message.identity_pb2 as identity_pb2
import nanoswap.message.lookup_pb2 as lookup_pb2
from models.return_types import NewCreditIdentity

def write_identity(id_content: str, id_type: int) -> NewCreditIdentity:
    # write identity
    identity = utils.new_identity(
        id_type,
        id_content
    )
    ipfs.write(identity.filename, identity.data)
    print(f"credit id created: {identity.credit_id}")
    return identity

def read_identity(filename):
    # read identity
    result = ipfs.read(filename, identity_pb2.Identity())
    print(f"read ssn: {result.id_field_content}")

def write_lookup(data, credit_id):
    # write lookup
    response = utils.new_lookup(data, credit_id)
    ipfs.write(response['filename'], response['data'])
    return response

def read_lookup(filename):
    # read lookup
    response = ipfs.read(filename, lookup_pb2.Lookup())
    print(f"read credit id: {response.credit_identity}")
