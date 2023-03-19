import uuid

import nanoswap.message.identity_pb2 as identity_pb2
import nanoswap.message.lookup_pb2 as lookup_pb2

def new_identity(field_type, field_value):
    credit_id = uuid.uuid4()
    filename = 'identity.' + str(credit_id)
    data = identity_pb2.Identity(
        id_field_type = field_type,
        id_field_content = field_value
    )

    # TODO: use pydantic structs instead of dict return types
    return {
        "credit_id": credit_id,
        "filename": filename,
        "data": data
    }

def new_lookup(identity, credit_id):
    filename = f"lookup.{identity.id_field_type}.{identity.id_field_content}.{str(credit_id)}"
    data = lookup_pb2.Lookup(
        credit_identity = str(credit_id)
    )

    return {
        "filename": filename,
        "data": data
    }
