import datetime
from google.protobuf.timestamp_pb2 import Timestamp

import nanoswap.message.identity_pb2 as identity_pb2
import nanoswap.message.loan_pb2 as loan_pb2

def get_filename(identity: identity_pb2.Identity) -> str:
    """
    Generate the filename for an identity

    Args:
        identity (identity_pb2.Identity): An object containing the id value and id type

    Returns:
        str: The filename to use in ipfs
    """
    return f"lookup.{identity.id_field_type}.{identity.id_field_content}"

def sign_loan(loan):
    loan.borrower_signature = "adsf"
    loan.lender_signature = "asdf"
    return loan

def create_payment_schedule(amount, interest_rate, total_duration, payment_wallet):
    timestamp = Timestamp()
    timestamp.FromDatetime(datetime.datetime.now() + total_duration)
    schedule = loan_pb2.PaymentSchedule(
        amount_due = amount,
        due_date = timestamp,
        payment_wallet = payment_wallet,
        status = loan_pb2.PaymentStatus.DUE
    )
    print(schedule)
    return [schedule]
