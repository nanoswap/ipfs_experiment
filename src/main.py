from faker import Faker
import datetime
import nanoswap.enum.issuers_pb2 as issuers_pb2
from models.loan_payment import LoanPayment
from models.loan import Loan
from models.wallet import Account
from models.identity import CreditId

def loan_test():

    Faker.seed(0)
    fake = Faker()

    # create fake users
    fake_users = [
        CreditId(fake.ssn(), issuers_pb2.Issuer.USA_SSN)
        for _ in range(2)
    ]

    # create a loan between two users
    borrower = fake_users[0].credit_identity
    lender = fake_users[1].credit_identity
    loan = Loan(
        borrower = borrower,
        lender = lender,
        amount = 100,
        interest = 1.05,
        day_count = 10,
        payment_interval_count = 10
    )

    # simulate the borrower making a payment

    # get the loans for the borrower
    loan_payments = LoanPayment.query_borrower_or_lender(lender_id = None, borrower_id = borrower)
    loan_payments = LoanPayment.flatten_query_results(loan_payments)
    loan_df = LoanPayment.to_dataframe(loan_payments)
    print(loan_df)

    # make a payment
    next_payment = LoanPayment.get_earliest_due(loan_payments)
    print("Next payment due: ", datetime.datetime.fromtimestamp(next_payment.reader.due_date.ToSeconds()))

    # clean up: delete loan files (for repeatable testing/debugging)
    for payment in loan_payments:
        payment.delete()

def nano_test():
    # create two accounts
    account1 = Account('nano_1111111111111111111111111111111111111111111111111111hifc8npp')
    account2 = Account('nano_33333333333333333333333333333333333333333333333333333333333333')

    # check account balances before transfer
    print(f"account1 balance: {account1.balance}")
    print(f"account2 balance: {account2.balance}")

    # send 1 XNO from account1 to account2
    send_block = account1.send(destination=account2.address, amount=1)

    # wait for confirmation
    confirmed_block = account1.receive()

    # check account balances after transfer
    print(f"account1 balance: {account1.balance}")
    print(f"account2 balance: {account2.balance}")

if __name__ == "__main__":
    # loan_test()
    nano_test()
