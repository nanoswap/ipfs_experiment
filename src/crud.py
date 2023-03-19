import uuid
import ipfs
import utils

import nanoswap.message.identity_pb2 as identity_pb2
from models.return_types import NewCreditIdentity, NewLookup

def write_identity(id_content: str, id_type: int) -> NewCreditIdentity:
    """
    Create a new credit identity and write it to ipfs

    Args:
        id_content (str): The value of the id
        id_type (int): The kind of id

    Returns:
        NewCreditIdentity: The generated credit_id and it's corresponding data
    """
    identity = utils.new_identity(
        id_type,
        id_content
    )
    ipfs.write(identity.filename, identity.data)
    return identity

def write_lookup(identity: identity_pb2.Identity, credit_id: uuid.UUID) -> NewLookup:
    """
    Create the lookup data corresponding to a credit identity.
    Add that lookup data to ipfs.

    Args:
        identity (identity_pb2.Identity): The credit identity data to generate lookup data from
        credit_id (uuid.UUID): The credit identity uuid corresponding to the identity object

    Returns:
        NewLookup: The generated filename and the lookup data content
    """
    lookup = utils.new_lookup(identity, credit_id)
    ipfs.write(lookup.filename, lookup.data)
    return lookup
