import datetime
from typing import List
from google.protobuf.timestamp_pb2 import Timestamp

import nanoswap.message.identity_pb2 as identity_pb2
import nanoswap.message.loan_pb2 as loan_pb2

import sys

def get_credit_filename(identity: identity_pb2.Identity) -> str:
    """
    Generate the filename for an identity

    Args:
        identity (identity_pb2.Identity): An object containing the id value and id type

    Returns:
        str: The filename to use in ipfs
    """
    return f"identity/{identity.id_field_type}.{identity.id_field_content}"

def create_payment_schedule(
        amount: int, interest_rate: float, total_duration: datetime.timedelta, number_of_payments: int
    ) -> List[loan_pb2.LoanPayment]:
    """
    Generate a list of loan payment objects based on some initial loan parameters

    Args:
        amount (int): The amount of the loan (before interest)
        interest_rate (float): The interest rate of the loan in decimal (ex: 1.05 is 5%)
        total_duration (datetime.timedelta): The time that the borrower has to finish all repayments
        number_of_payments (int): The number of payments to break up the loan into

    Returns:
        List[loan_pb2.LoanPayment]: The derived payment schedule with how much to pay on what days
    """
    assert interest_rate > 1

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

def get_next_payment_due(payment_schedule: List[loan_pb2.LoanPayment]) -> loan_pb2.LoanPayment:
    """
    Filter the payment schedule to find the next upcoming payment

    Args:
        payment_schedule (List[loan_pb2.LoanPayment]): The full payment schedule for the loan

    Returns:
        loan_pb2.LoanPayment: The next upcoming payment
    """
    next_due_seconds = sys.maxsize
    next_due_payment = None
    for payment in payment_schedule:
        # TODO: if the transaction exists, check if it is valid, complete, and for the correct time / amount
        # (using XNO RPC calls)
        if payment['data'].due_date.ToSeconds() < next_due_seconds and not payment['data'].transaction:
            next_due_seconds = payment['data'].due_date.ToSeconds()
            next_due_payment = payment

    return next_due_payment
