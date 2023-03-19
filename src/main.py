from faker import Faker

import nanoswap.enum.issuers_pb2 as issuers_pb2
import nanoswap.message.identity_pb2 as identity_pb2
import nanoswap.message.lookup_pb2 as lookup_pb2

import crud
import ipfs

# Faker.seed(0)
fake = Faker()

def run():
    # create fake data for a hypothetical user
    ssn = fake.ssn()
    print(f"writing ssn: {ssn}")

    # write their ID data to the credit identity system
    identity = crud.write_identity(ssn, issuers_pb2.Issuer.UNITED_STATES_AMERICA___FEDERAL___SOCIAL_SECURITY_NUMBER)
    print(f"credit id created: {identity.credit_id}")

    # read back the file we just wrote
    identity_from_ipfs = ipfs.read(identity.filename, identity_pb2.Identity())
    print(f"read ssn: {identity_from_ipfs.id_field_content}")

    # create a lookup record for the ID
    # TODO: do this with a kafka listener or something so it can be retried in an event queue
    lookup = crud.write_lookup(identity.data, identity.credit_id)

    # read the lookup record back to check that it worked
    lookup_from_ipfs = ipfs.read(lookup.filename, lookup_pb2.Lookup())
    print(f"read credit id: {lookup_from_ipfs.credit_identity}")

if __name__ == "__main__":
    run()
