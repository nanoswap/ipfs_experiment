import uuid
from faker import Faker

import nanoswap.enum.issuers_pb2 as issuers_pb2
import nanoswap.message.identity_pb2 as identity_pb2
import nanoswap.message.lookup_pb2 as lookup_pb2

import crud
import ipfs

# Faker.seed(0)
fake = Faker()

def run():
    ssn = fake.ssn()
    print(f"writing ssn: {ssn}")

    identity = crud.write_identity(ssn, issuers_pb2.Issuer.UNITED_STATES_AMERICA___FEDERAL___SOCIAL_SECURITY_NUMBER)
    identity_from_ipfs = ipfs.read(identity.filename, identity_pb2.Identity())
    print(f"read ssn: {identity_from_ipfs.id_field_content}")

    lookup = crud.write_lookup(identity.data, identity.credit_id)
    lookup_from_ipfs = ipfs.read(lookup.filename, lookup_pb2.Lookup())
    print(f"read credit id: {lookup_from_ipfs.credit_identity}")

if __name__ == "__main__":
    run()
