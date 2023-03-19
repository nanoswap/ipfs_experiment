import uuid

import nanoswap.message.identity_pb2 as identity_pb2

def new_identity(field_type, field_value):
    credit_id = uuid.uuid4()
    filename = 'identity.' + str(credit_id)
    data = identity_pb2.Identity(
        id_field_type = field_type,
        id_field_content = field_value
    )
    return filename, data
