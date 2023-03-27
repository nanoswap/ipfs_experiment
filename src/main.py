from faker import Faker
import datetime
import uuid

import nanoswap.enum.issuers_pb2 as issuers_pb2
import nanoswap.enum.chains_pb2 as chains_pb2
import nanoswap.enum.currency_pb2 as currency_pb2
import nanoswap.message.identity_pb2 as identity_pb2
import nanoswap.message.loan_pb2 as loan_pb2

import crud
import utils

Faker.seed(0)
fake = Faker()

def create_user():
    # create fake data for a hypothetical user
    identity = identity_pb2.Identity(
        id_field_content = fake.ssn(),
        id_field_type = issuers_pb2.Issuer.UNITED_STATES_AMERICA___FEDERAL___SOCIAL_SECURITY_NUMBER
    )

    # get the credit identity for the fake user
    return crud.get_credit_id(identity)

def run():

    # create fake users
    fake_users = [create_user() for _ in range(10)]
    print(fake_users)

    # create a loan
    amount = 100
    loan = loan_pb2.Loan(
        id = str(uuid.uuid4()),
        borrower_identity = str(fake_users[0].id),
        lender_identity = str(fake_users[1].id),
        chain = chains_pb2.OFF_CHAIN,
        currency = currency_pb2.XNO,
        amount = amount,
        status = loan_pb2.LoanStatus.CREATED,
        payment_schedule = utils.create_payment_schedule(amount, 1.05, datetime.timedelta(days=100), 10, "123")
    )

if __name__ == "__main__":
    run()
