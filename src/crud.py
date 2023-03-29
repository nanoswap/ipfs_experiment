import uuid
import ipfs
import utils
import datetime

import nanoswap.message.identity_pb2 as identity_pb2
import nanoswap.message.lookup_pb2 as lookup_pb2
import nanoswap.message.loan_pb2 as loan_pb2
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
        ipfs.add(filename, lookup_pb2.Lookup(
            credit_identity = str(credit_id)
        ))

        return CreditId(credit_id, CreditIdStatus.CREATED)
    
    else:

        # read the existing identity
        ipfs_data = ipfs.read(filename, lookup_pb2.Lookup())
        return CreditId(uuid.UUID(ipfs_data.credit_identity), CreditIdStatus.RETRIEVED)

def create_loan(borrower, lender, amount, interest, day_count, payment_interval_count):
    loan_id = str(uuid.uuid4())
    payment_schedule = utils.create_payment_schedule(
        amount,
        interest,
        datetime.timedelta(days=day_count),
        payment_interval_count
    )

    for payment in payment_schedule:
        payment_id = str(uuid.uuid4())
        filename = utils.get_loan_payment_filename(loan_id, borrower, lender, payment_id)
    
        if not ipfs.does_file_exist(filename):
            ipfs.add(filename, payment)

    return payment_schedule

def get_loans(borrower):
    """
    Get the loan_id ' s for a borrower

    Args:
        borrower (_type_): _description_

    Returns:
        _type_: _description_
    """

    # read the loan metadata from ipfs
    files = ipfs.list_files(f"loan/")

    # parse the loan metadata from the filename
    # filename format: ['borrower_<borrower_id>.lender_<lender_id>.loan_<loan_id>']
    loan_metadata = [
        {
            "borrower": filename.split('.')[0].split("_")[1],
            "lender": filename.split('.')[1].split("_")[1],
            "loan": filename.split('.')[2].split("_")[1],
            "payment": filename.split('.')[3].split("_")[1],
            "filename": filename
        } for filename in files if filename
    ]
    
    # filter for the loans for this borrower
    loan_files = [
        loan for loan in loan_metadata
        if loan["borrower"] == str(borrower)
    ]
    
    # read the full loan data for their loans
    response = []
    for loan in loan_files:
        response.append({
            "metadata": loan,
            "data": ipfs.read(f"loan/{loan['filename']}", loan_pb2.LoanPayment())
        })
    
    return response
