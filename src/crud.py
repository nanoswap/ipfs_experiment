import uuid
import ipfs
import utils

import nanoswap.message.identity_pb2 as identity_pb2
import nanoswap.message.lookup_pb2 as lookup_pb2
from models.return_types import CreditId, CreditIdStatus

def get_credit_id(identity: identity_pb2.Identity) -> CreditId:
    """
    For the given identity (id_value, id_type), either:
        1. retrieve the credit id corresponding to this identity
    or:
        2. create a new credit id for this identity
    
    Args:
        id_content (str): The value of the id
        id_type (int): The kind of id

    Returns:
        CreditId: The credit_id for the identity and metadata about if it is new to the system
    """
    filename = utils.get_filename(identity)
    print(filename)

    # check if the identity already exists
    file_exists = ipfs.does_file_exist(filename)
    if not file_exists:

        # generate a new credit id
        credit_id = uuid.uuid4()

        # wrap it in a protobuf and write it to ipfs
        ipfs.write(filename, lookup_pb2.Lookup(
            credit_identity = str(credit_id)
        ))

        return CreditId(credit_id, CreditIdStatus.CREATED)
    
    else:

        # read the existing identity
        ipfs_data = ipfs.read(filename, lookup_pb2.Lookup())
        return CreditId(uuid.UUID(ipfs_data.credit_identity), CreditIdStatus.RETRIEVED)
