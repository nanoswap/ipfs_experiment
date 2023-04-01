from typing import List

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
