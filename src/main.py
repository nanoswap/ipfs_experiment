from faker import Faker
import copy

import nanoswap.enum.issuers_pb2 as issuers_pb2
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

def make_payment(borrower, loan):

    # get the next due payment
    next_payment = utils.get_next_payment_due(loan.payment_schedule)

    # update the payment object in memory
    next_payment = utils.update_payment(next_payment, loan_pb2.PaymentStatus.PAID_ON_TIME, "123")

    # upsert the updated payment object into the payment schedule
    payment_schedule = copy.deepcopy(loan.payment_schedule)
    # assignment of repeated fields is not possible,
    # so we have to copy it, delete it, and then reassign it
    del loan.payment_schedule[:]
    loan.payment_schedule.extend(utils.upsert_payment(next_payment, payment_schedule))
    print(loan.payment_schedule)

    # overwrite the data in ipfs to publicize it

    # TODO: redo how this is done to make it simpler.
    #   1. Give each payment in the schedule an ID, remove trx_id and payment status
    #   2. Add the loan id and the payment schedule ID in the credit event key
    #   3. send the payment status and trx id in the credit event
    # the loan file should not need to be written to for every payment

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
    make_payment(borrower, loans[0])

if __name__ == "__main__":
    run()
