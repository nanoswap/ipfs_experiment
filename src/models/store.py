from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Iterator, List, Literal
from uuid import UUID
import uuid
import utils
from google.protobuf.message import Message
from google.protobuf.timestamp_pb2 import Timestamp
from models.file import File
import sys
import pandas as pd
from datetime import datetime
from models.index import Index


@dataclass
class Store(File):
    index: Index
    writer: Message
    reader: Message

    def __init__(self, index: Index, writer: Message = None, reader: Message = None) -> None:
        self.index = index
        self.writer = writer
        self.reader = reader
    
    # @staticmethod
    # def to_dataframe(data: List[Store]) -> pd.DataFrame:
    #     """
    #     Convert a list of Store objects to a pandas dataframe.
    #     This function will read the data for each file, and include it in the result.

    #     Args:
    #         data (List[Store]): The list of Store objects

    #     Returns:
    #         pd.DataFrame: The dataframe with the loan payment data from ipfs
    #     """
    #     pandas_input = {'borrower': [], 'lender': [], 'loan': [], 'payment': [], 'amount_due': [], 'due_date': [], 'state': []}
    #     for record in data:
    #         record.read()  # read the file content from ipfs
    #         pandas_input['borrower'].append(payment.borrower_id)
    #         pandas_input['lender'].append(payment.lender_id)
    #         pandas_input['loan'].append(payment.loan_id)
    #         pandas_input['payment'].append(payment.payment_id)
    #         pandas_input['amount_due'].append(payment.reader.amount_due)
    #         pandas_input['due_date'].append(datetime.fromtimestamp(payment.reader.due_date.ToSeconds()))
        
    #     # load the data into a pandas dataframe
    #     return pd.DataFrame.from_dict(pandas_input)

    @staticmethod
    def query(index: Index) -> List[Store]:
        path = index.get_filename()

        result = []
        for filename in utils.list_files(path):
            has_prefix = index.prefix is not None

            next_index = Index.from_filename(
                f"{path}/{filename}",
                has_prefix = has_prefix
            )

            # check for partial queries
            if index.is_partial() and not index.matches(next_index):
                continue
            
            # Check for subdirectories
            if [filename] == utils.list_files(f"{path}/{filename}"):
                # Base case, no subdirectories found
                result.append(Store(index = next_index))

            else:
                result += Store.query(index = next_index)

        return result
            

    @staticmethod
    def query_borrower_and_lender(
        borrower_id: UUID,
        lender_id: UUID
    ) -> Dict[UUID, Iterator[LoanPayment]]:
        """
        Get all of the loan payments for this borrower and lender

        Args:
            borrower_id (UUID): The borrower credit identity
            lender_id (UUID): The lender credit identity

        Returns:
            Dict[UUID, List[LoanPayment]]: A dictionary of (key: loan id, value: the list of loan payments)
        """
        path = f"loan/borrower_{borrower_id}.lender_{lender_id}"
        result = {}
        # list the loans for this borrower/lender pair
        for filename in ipfs.list_files(path):
            if filename:
                # get the loan payment data for each loan
                loan_id = filename.split("_")[1]
                result[loan_id] = LoanPayment.query(borrower_id, lender_id, loan_id)
        
        return result

    @staticmethod
    def query_borrower_or_lender(
        borrower_id: UUID = None,
        lender_id: UUID = None
    ) -> Dict[str, Dict[UUID, Iterator[LoanPayment]]]:
        """
        Get the loan data for a borrower or a lender

        One of (borrower_id, lender_id) is required.
        If both are provided, get the union of their data:
            (data where x is borrower UNION data where y is lender)

        Args:
            borrower_id (UUID, optional): The borrower credit identity. Defaults to None.
            lender_id (UUID, optional): The lender credit identity. Defaults to None.

        Returns:
            Dict[str, Dict[UUID, Iterator[LoanPayment]]]: A dictionary of 
                (
                    key: borrower_<borrower_id>.lender_<lender_id>,
                    value: A dictionary of (key: loan id, value: the list of loan payments)
                )
        """
        assert borrower_id or lender_id

        result = {}
        # list the (lender, borrower) pairs
        for file in ipfs.list_files(f"loan/"):

            if not file:
                continue

            # parse the directory name metadata
            filename_borrower_id = file.split(".")[0].split("_")[1]
            filename_lender_id = file.split(".")[1].split("_")[1]

            if borrower_id and filename_borrower_id == str(borrower_id):
                # get the loan data for this directory, with this borrower
                result[file] = LoanPayment.query_borrower_and_lender(filename_borrower_id, filename_lender_id)

            if lender_id and filename_lender_id == str(lender_id):
                # get the loan data for this directory, with this lender
                result[file] = LoanPayment.query_borrower_and_lender(filename_borrower_id, filename_lender_id)

        return result

    @staticmethod
    def flatten_query_results(loan_payments: Dict[str, Dict[UUID, Iterator[LoanPayment]]]) -> List[LoanPayment]:
        """
        Take the nested output from `query_borrower_or_lender` and turn it into
        a flat list of LoanPayment data.

        Args:
            loan_payments (Dict[str, Dict[UUID, Iterator[LoanPayment]]]): The loan payment metadata

        Returns:
            List[LoanPayment]: The list of LoanPayments
        """
        result = []
        # borrower_<borrower_id>.lender_<lender_id> folder
        for borrower_lender in loan_payments:
            # loan_id folder
            for loan in loan_payments[borrower_lender]:
                # payment_id folder
                for payment in loan_payments[borrower_lender][loan]:
                    result.append(payment)
        
        return result

    @staticmethod
    def get_earliest_due(loan_payments: List[LoanPayment], read_from_ipfs: bool = False) -> LoanPayment:
        """
        For the list of loan payments, get the one with the earliest due date

        Args:
            loan_payments (List[LoanPayment]): The list of LoanPayment's to filter
            read_from_ipfs (bool): If true, call `.read()` on each loan payment. Defaults to False.

        Returns:
            LoanPayment: The earliest LoanPayment object.
        """
        earliest = sys.maxsize
        result = None
        for payment in loan_payments:
            if read_from_ipfs:
                payment.read()

            if payment.reader.due_date.ToSeconds() < earliest:
                earliest = payment.reader.due_date.ToSeconds()
                result = payment
        
        return result
