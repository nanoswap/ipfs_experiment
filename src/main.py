from faker import Faker

import nanoswap.enum.issuers_pb2 as issuers_pb2
import nanoswap.message.identity_pb2 as identity_pb2

import crud

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

    # create a loan between two users
    borrower = fake_users[0].id
    lender = fake_users[1].id
    loan = crud.create_loan(
        borrower = borrower,
        lender = lender,
        amount = 100,
        interest = 1.05,
        day_count = 10,
        payment_interval_count = 10
    )

    # simulate the borrower making a payment

    # get the loans for the borrower
    loans = crud.get_loans(borrower)

    # get the next due payment
    utils.get_next_payment(loans[0].payment_schedule)

if __name__ == "__main__":
    run()
