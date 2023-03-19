import uuid
from faker import Faker

import nanoswap.enum.issuers_pb2 as issuers_pb2

import crud

# Faker.seed(0)
fake = Faker()

def run():
    ssn = fake.ssn()
    print(f"writing ssn: {ssn}")

    identity = crud.write_identity(ssn, issuers_pb2.Issuer.UNITED_STATES_AMERICA___FEDERAL___SOCIAL_SECURITY_NUMBER)
    crud.read_identity(identity.filename)
    lookup_response = crud.write_lookup(identity.data, identity.credit_id)
    crud.read_lookup(lookup_response.filename)

if __name__ == "__main__":
    run()
