from typing import List
import uuid
import ipfs
import utils

from models.return_types import CreditId, CreditIdStatus

import nanoswap.message.identity_pb2 as identity_pb2
import nanoswap.message.loan_pb2 as loan_pb2

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
        ipfs.add(filename, identity_pb2.Lookup(
            credit_identity = str(credit_id)
        ))

        return CreditId(credit_id, CreditIdStatus.CREATED)
    
    else:

        # read the existing identity
        ipfs_data = ipfs.read(filename, identity_pb2.Lookup())
        return CreditId(uuid.UUID(ipfs_data.credit_identity), CreditIdStatus.RETRIEVED)

# def get_loan_metadata() -> List[LoanMetadata]:
#     """
#     Get all the loan metadata

#     Returns:
#         List[LoanMetadata]: The complete list of loan metadata
#     """

#     # read the loan metadata from ipfs
#     files = ipfs.list_files(f"loan/")

#     # parse the loan metadata from the filename
#     # filename format: ['borrower_<borrower_id>.lender_<lender_id>.loan_<loan_id>']
#     return [
#         {
#             "borrower": filename.split('.')[0].split("_")[1],
#             "lender": filename.split('.')[1].split("_")[1],
#             "loan": filename.split('.')[2].split("_")[1],
#             "payment": filename.split('.')[3].split("_")[1],
#             "filename": filename
#         } for filename in files if filename
#     ]

# def get_loan_data(loans: List[LoanMetadata]) -> List[LoanResponse]:
#     """
#     For each loan filename, read the data for that file from ipfs

#     Args:
#         loans (List[LoanMetadata]): The list of loan metadata from `get_loan_metadata`

#     Returns:
#         List[LoanResponse]: The list of loan metadata and corresponding data
#     """
#     response = []
#     for loan in loans:
#         response.append({
#             "metadata": loan,
#             "data": ipfs.read(f"loan/{loan['filename']}", loan_pb2.LoanPayment())
#         })
    
#     return response

# def get_loans_for_borrower(borrower: str) -> List[LoanResponse]:
#     """
#     Get the loans for a borrower

#     Args:
#         borrower (str): The borrower credit id to use in filtering

#     Returns:
#         List[LoanResponse]: The list of loans corresponding to the borrower
#     """

#     # filter for the loans for this borrower
#     loan_files = [
#         loan for loan in get_loan_metadata()
#         if loan["borrower"] == str(borrower)
#     ]
    
#     # read the full loan data for their loans
#     return get_loan_data(loan_files)


# def get_loans_for_lender(lender: str) -> List[LoanResponse]:
#     """
#     Get the loans for a lender

#     Args:
#         lender (str): The lender credit id to use in filtering

#     Returns:
#         List[LoanResponse]: The list of loans corresponding to the lender
#     """
    
#     # filter for the loans for this lender
#     loan_files = [
#         loan for loan in get_loan_metadata()
#         if loan["lender"] == str(lender)
#     ]
    
#     # read the full loan data for their loans
#     return get_loan_data(loan_files)

# def get_loan(loan: str) -> List[LoanResponse]:
#     """
#     Get the loan data for a loan id

#     Args:
#         loan (str): The loan uuid to use in filtering

#     Returns:
#         List[LoanResponse]: The list of loans corresponding to the lender
#     """
    
#     # filter for the loans for the loan id
#     loan_files = [
#         loan for loan in get_loan_metadata()
#         if loan["loan"] == str(loan)
#     ]
    
#     # read the full loan data for the loans
#     return get_loan_data(loan_files)
