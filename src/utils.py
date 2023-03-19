import uuid

import nanoswap.message.identity_pb2 as identity_pb2
import nanoswap.message.lookup_pb2 as lookup_pb2
from models.return_types import NewCreditIdentity, NewLookup

def new_identity(field_type, field_value) -> NewCreditIdentity:
    credit_id = uuid.uuid4()
    filename = 'identity.' + str(credit_id)
    data = identity_pb2.Identity(
        id_field_type = field_type,
        id_field_content = field_value
    )

    return NewCreditIdentity(credit_id, filename, data)

def new_lookup(identity: identity_pb2.Identity, credit_id: uuid.UUID) -> NewLookup:
    filename = f"lookup.{identity.id_field_type}.{identity.id_field_content}.{str(credit_id)}"
    data = lookup_pb2.Lookup(
        credit_identity = str(credit_id)
    )

    return NewLookup(filename, data)
