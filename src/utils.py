import nanoswap.message.identity_pb2 as identity_pb2

def get_credit_filename(identity: identity_pb2.Identity) -> str:
    """
    Generate the filename for an identity

    Args:
        identity (identity_pb2.Identity): An object containing the id value and id type

    Returns:
        str: The filename to use in ipfs
    """
    return f"identity/{identity.id_field_type}.{identity.id_field_content}"
