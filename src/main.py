from faker import Faker

import nanoswap.enum.issuers_pb2 as issuers_pb2
import nanoswap.message.identity_pb2 as identity_pb2

import crud

Faker.seed(0)
fake = Faker()

def run():

    # create fake data for a hypothetical user
    identity = identity_pb2.Identity(
        id_field_content = fake.ssn(),
        id_field_type = issuers_pb2.Issuer.UNITED_STATES_AMERICA___FEDERAL___SOCIAL_SECURITY_NUMBER
    )
    print(f"writing ssn: {identity.id_field_content}")

    # get the credit identity for the fake user
    credit_id = crud.get_credit_id(identity)
    print(credit_id)

if __name__ == "__main__":
    run()
