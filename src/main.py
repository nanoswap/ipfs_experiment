import uuid
from faker import Faker

import nanoswap.enum.issuers_pb2 as issuers_pb2
import nanoswap.message.identity_pb2 as identity_pb2
import nanoswap.message.lookup_pb2 as lookup_pb2

import ipfs
import utils

# Faker.seed(0)
fake = Faker()

def write_identity(ssn):
    # write identity
    response = utils.new_identity(
        issuers_pb2.Issuer.UNITED_STATES_AMERICA___FEDERAL___SOCIAL_SECURITY_NUMBER,
        ssn
    )
    ipfs.write(response['filename'], response['data'])
    print(f"credit id created: {response['credit_id']}")
    return response

def read_identity(filename):
    # read identity
    result = ipfs.read(filename, identity_pb2.Identity())
    print(f"read ssn: {result.id_field_content}")

def write_lookup(data, credit_id):
    # write lookup
    response = utils.new_lookup(data, credit_id)
    ipfs.write(response['filename'], response['data'])
    return response

def read_lookup(filename):
    # read lookup
    response = ipfs.read(filename, lookup_pb2.Lookup())
    print(f"read credit id: {response.credit_identity}")

def run():
    ssn = fake.ssn()
    print(f"writing ssn: {ssn}")

    id_response = write_identity(ssn)
    read_identity(id_response['filename'])
    lookup_response = write_lookup(id_response['data'], id_response['credit_id'])
    read_lookup(lookup_response['filename'])

if __name__ == "__main__":
    run()
