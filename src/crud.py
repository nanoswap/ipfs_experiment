import uuid
import ipfs
import utils
import datetime

import nanoswap.message.identity_pb2 as identity_pb2
import nanoswap.message.lookup_pb2 as lookup_pb2
import nanoswap.message.loan_pb2 as loan_pb2
import nanoswap.enum.chains_pb2 as chains_pb2
import nanoswap.enum.currency_pb2 as currency_pb2
from models.return_types import CreditId, CreditIdStatus

def get_credit_id(identity: identity_pb2.Identity) -> CreditId:
    """
    For the given identity (id_value, id_type), either:
        1. retrieve the credit id corresponding to this identity
    or:
        2. create a new credit id for this identity
    
    Args:
        id_content (str): The value of the id
        id_type (int): The kind of id

    Returns:
        CreditId: The credit_id for the identity and metadata about if it is new to the system
    """
    filename = utils.get_credit_filename(identity)

    # check if the identity already exists
    file_exists = ipfs.does_file_exist(filename)
    if not file_exists:

        # generate a new credit id
        credit_id = uuid.uuid4()

        # wrap it in a protobuf and write it to ipfs
        ipfs.write(filename, lookup_pb2.Lookup(
            credit_identity = str(credit_id)
        ))

        return CreditId(credit_id, CreditIdStatus.CREATED)
    
    else:

        # read the existing identity
        ipfs_data = ipfs.read(filename, lookup_pb2.Lookup())
        return CreditId(uuid.UUID(ipfs_data.credit_identity), CreditIdStatus.RETRIEVED)

def create_loan(borrower, lender, amount, interest, day_count, payment_interval_count):
    loan_id = str(uuid.uuid4())
    filename = utils.get_loan_filename(loan_id, borrower, lender)

    # TODO:
    #   - call `ipfs.mkdir` to make a folder for the user's loans
    #   - update `utils.get_loan_filename` to use directory format

    loan = loan_pb2.Loan(
        borrower_identity = str(borrower),
        lender_identity = str(lender),
        chain = chains_pb2.OFF_CHAIN,
        currency = currency_pb2.XNO,
        amount = amount,
        status = loan_pb2.LoanStatus.CREATED,
        payment_schedule = utils.create_payment_schedule(
            amount,
            interest,
            datetime.timedelta(days=day_count),
            payment_interval_count,
            "123"
        )
    )

    ipfs.write(filename, loan)
    return loan

def get_loans(borrower):
    ipfs.list_files(f"loan.borrower_{borrower}")
