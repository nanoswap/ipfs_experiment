import uuid

import nanoswap.message.identity_pb2 as identity_pb2
import nanoswap.message.lookup_pb2 as lookup_pb2
from models.return_types import NewCreditIdentity, NewLookup

def new_identity(field_type: int, field_value: str) -> NewCreditIdentity:
    """
    Issue a new credit identity uuid.
    Generate the filename for the new profile (based on credit_id).
    Construct a protobuf model with the identity data.

    Args:
        field_type (int): The kind of id
        field_value (str): The value of the id

    Returns:
        NewCreditIdentity: The generated credit_id and it's corresponding data
    """
    credit_id = uuid.uuid4()
    filename = 'identity.' + str(credit_id)
    data = identity_pb2.Identity(
        id_field_type = field_type,
        id_field_content = field_value
    )

    return NewCreditIdentity(credit_id, filename, data)

def new_lookup(identity: identity_pb2.Identity, credit_id: uuid.UUID) -> NewLookup:
    """
    Create a new lookup entry for a credit identity.
    Generate the filename for the lookup (based on the id type and id value).
    Construct a protobuf model to serialize the credit identity uuid.

    Args:
        identity (identity_pb2.Identity): The id record associated to the credit identity
        credit_id (uuid.UUID): The credit identity to add a lookup for

    Returns:
        NewLookup: The generated filename and the lookup data content
    """
    filename = f"lookup.{identity.id_field_type}.{identity.id_field_content}"
    data = lookup_pb2.Lookup(
        credit_identity = str(credit_id)
    )

    return NewLookup(filename, data)
