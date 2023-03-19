from faker import Faker

import nanoswap.enum.issuers_pb2 as issuers_pb2
import nanoswap.message.identity_pb2 as identity_pb2

import ipfs
import utils

Faker.seed(0)
fake = Faker()


def run():
    ssn = fake.ssn()
    print(f"writing ssn: {ssn}")
    filename, data = utils.new_identity(
        issuers_pb2.Issuer.UNITED_STATES_AMERICA___FEDERAL___SOCIAL_SECURITY_NUMBER,
        ssn
    )
    ipfs.write(filename, data)
    result = ipfs.read(filename, identity_pb2.Identity())
    print(f"read ssn: {result.id_field_content}")

if __name__ == "__main__":
    run()
