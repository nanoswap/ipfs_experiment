import uuid
from faker import Faker

import nanoswap.enum.issuers_pb2 as issuers_pb2
import nanoswap.message.identity_pb2 as identity_pb2
import nanoswap.message.lookup_pb2 as lookup_pb2

import ipfs
import utils

# Faker.seed(0)
fake = Faker()


def run():
    ssn = fake.ssn()
    print(f"writing ssn: {ssn}")

    # write identity
    credit_id, filename, data = utils.new_identity(
        issuers_pb2.Issuer.UNITED_STATES_AMERICA___FEDERAL___SOCIAL_SECURITY_NUMBER,
        ssn
    )
    ipfs.write(filename, data)
    print(f"credit id created: {credit_id}")

    # read identity
    result = ipfs.read(filename, identity_pb2.Identity())
    print(f"read ssn: {result.id_field_content}")

    # write lookup
    filename, data = utils.new_lookup(data, credit_id)
    ipfs.write(filename, data)

    # read lookup
    result = ipfs.read(filename, lookup_pb2.Lookup())
    print(f"read credit id: {result.credit_identity}")

if __name__ == "__main__":
    run()
