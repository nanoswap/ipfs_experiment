import datetime
from google.protobuf.timestamp_pb2 import Timestamp

import nanoswap.message.identity_pb2 as identity_pb2
import nanoswap.message.loan_pb2 as loan_pb2

def get_credit_filename(identity: identity_pb2.Identity) -> str:
    """
    Generate the filename for an identity

    Args:
        identity (identity_pb2.Identity): An object containing the id value and id type

    Returns:
        str: The filename to use in ipfs
    """
    return f"identity/{identity.id_field_type}.{identity.id_field_content}"

def get_loan_filename(loan_id, borrower, lender):
    return f"loan/borrower_{borrower}.lender_{lender}.loan_{loan_id}"

def sign_loan(loan):
    loan.borrower_signature = "adsf"
    loan.lender_signature = "asdf"
    return loan

def create_payment_schedule(amount, interest_rate, total_duration, number_of_payments, payment_wallet):

    total_amount_due = amount * interest_rate
    amount_due_each_payment = int(total_amount_due / number_of_payments)
    first_payment = datetime.datetime.now()
    schedule = []

    for payment_interval in range(number_of_payments):
        timestamp = Timestamp()
        timestamp.FromDatetime(first_payment + payment_interval * total_duration)
        schedule.append(loan_pb2.PaymentSchedule(
            amount_due = amount_due_each_payment,
            due_date = timestamp,
            payment_wallet = payment_wallet,
            status = loan_pb2.PaymentStatus.DUE
        ))

    return schedule

def get_next_payment(payment_schedule):
    pass
