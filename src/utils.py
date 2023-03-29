import datetime
from google.protobuf.timestamp_pb2 import Timestamp

import nanoswap.message.identity_pb2 as identity_pb2
import nanoswap.message.loan_pb2 as loan_pb2

import sys
import copy

def get_credit_filename(identity: identity_pb2.Identity) -> str:
    """
    Generate the filename for an identity

    Args:
        identity (identity_pb2.Identity): An object containing the id value and id type

    Returns:
        str: The filename to use in ipfs
    """
    return f"identity/{identity.id_field_type}.{identity.id_field_content}"

def get_loan_filename(loan_id, borrower, lender, payment_id):
    return f"loan/borrower_{borrower}.lender_{lender}.loan_{loan_id}.payment_{payment_id}"

def create_payment_schedule(amount, interest_rate, total_duration, number_of_payments):

    total_amount_due = amount * interest_rate
    amount_due_each_payment = int(total_amount_due / number_of_payments)
    first_payment = datetime.datetime.now()
    schedule = []

    for payment_interval in range(number_of_payments):
        timestamp = Timestamp()
        timestamp.FromDatetime(first_payment + payment_interval * total_duration)
        schedule.append(loan_pb2.LoanPayment(
            amount_due = amount_due_each_payment,
            due_date = timestamp
        ))

    return schedule

def get_next_payment_due(payment_schedule):
    next_due_seconds = sys.maxsize
    next_due_payment = None
    for payment in payment_schedule:
        if payment['data'].due_date.ToSeconds() < next_due_seconds and not payment['data'].transaction:
            next_due_seconds = payment['data'].due_date.ToSeconds()
            next_due_payment = payment

    return next_due_payment

def update_payment(payment, status, transaction_id):
    payment.status = status
    payment.transaction = transaction_id
    return payment
