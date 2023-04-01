from faker import Faker

import nanoswap.enum.issuers_pb2 as issuers_pb2
import nanoswap.message.identity_pb2 as identity_pb2
import nanoswap.message.loan_pb2 as loan_pb2

from models.loan_payment import LoanPayment
from models.loan import Loan

import crud
import utils
import ipfs

Faker.seed(0)
fake = Faker()

def create_user():
    # create fake data for a hypothetical user
    identity = identity_pb2.Identity(
        id_field_content = fake.ssn(),
        id_field_type = issuers_pb2.Issuer.USA_SSN
    )

    # get the credit identity for the fake user
    return crud.get_credit_id(identity)

# def make_payment(loan):

#     # get the next due payment
#     next_payment = utils.get_next_payment_due(loan)

#     # TODO: print "your next payment is due <date> for <amount> XNO"

#     # after the payment is confirmed, add it to the protobuf object
#     paid_payment = loan_pb2.LoanPayment(
#         amount_due = next_payment["data"].amount_due,
#         due_date = next_payment["data"].due_date,
#         transaction = "123"
#     )

#     # upsert the updated payment object into the payment schedule
#     ipfs.write("loan/" + next_payment["metadata"]["filename"], paid_payment)


def run():

    # create fake users
    fake_users = [create_user() for _ in range(2)]

    # create a loan between two users
    borrower = fake_users[0].id
    lender = fake_users[1].id
    loan = Loan(
        borrower = borrower,
        lender = lender,
        amount = 100,
        interest = 1.05,
        day_count = 10,
        payment_interval_count = 10
    )

    # TODO: visualize payment schedule

    # simulate the borrower making a payment

    # get the loans for the borrower
    # loans = crud.get_loans_for_borrower(borrower)

    # # make a payment
    # make_payment(loans)

if __name__ == "__main__":
    run()
