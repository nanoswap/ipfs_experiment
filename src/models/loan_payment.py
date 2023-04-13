from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Iterator, List, Literal
from uuid import UUID
import uuid
import nanoswap.message.loan_pb2 as loan_pb2
import ipfs
from google.protobuf.message import Message
from google.protobuf.timestamp_pb2 import Timestamp
from models.ipfs_file import IpfsFile
import sys
import pandas as pd
from datetime import datetime

@dataclass
class LoanPayment(IpfsFile):
    borrower_id: UUID
    lender_id: UUID
    payment_id: UUID
    loan_id: UUID
    filename: str
    writer: Message
    reader: Message = loan_pb2.LoanPayment()

    def __init__(
            self,
            borrower_id: UUID,
            lender_id: UUID,
            loan_id: UUID,
            payment_id: UUID = None,
            amount_due: int = None,
            due_date: Timestamp = None
        ) -> None:
        """
        Create a new Loan Payment
        
        Args:
            self (object): Static LoanPayment
            borrower_id (UUID): The borrower credit identity
            lender_id (UUID): The lender credit identity
            loan_id (UUID): The loan id
            payment_id (UUID, optional): The payment id. Defaults to None.
            amount_due (int, optional): The amount due. Defaults to None.
            due_date (Timestamp, optional): The date that the amount is due. Defaults to None.
        """

        self.borrower_id = borrower_id
        self.lender_id = lender_id
        self.loan_id = loan_id

        # generate a new payment_id if it wasn't provided
        self.payment_id = payment_id if payment_id else uuid.uuid4()
        self.filename = f"loan/borrower_{self.borrower_id}.lender_{self.lender_id}/loan_{self.loan_id}/payment_{self.payment_id}"

        if amount_due and due_date:
            # call .write() to write the new data
            self.writer = loan_pb2.LoanPayment(amount_due = amount_due, due_date = due_date)
        else:
            # call .read() to read the data for this filename
            self.filename = f"loan/borrower_{self.borrower_id}.lender_{self.lender_id}/loan_{self.loan_id}/payment_{self.payment_id}"
            self.writer = None

    @staticmethod
    def open(filename: str) -> LoanPayment:
        """
        Parse the filename into a LoanPayment object

        Args:
            filename (str): The filename to parse

        Returns:
            LoanPayment: The corresponding LoanPayment object
        """
        return LoanPayment(
            borrower_id=filename.split("/")[1].split(".")[0].split("_")[1],
            lender_id=filename.split("/")[1].split(".")[1].split("_")[1],
            loan_id=filename.split("/")[2].split("_")[1],
            payment_id=filename.split("/")[3].split("_")[1]
        )

    @staticmethod
    def to_dataframe(loan_payments: List[LoanPayment]) -> pd.DataFrame:
        """
        Convert a list of LoanPayments to a pandas dataframe.
        This function will read the data for each file, and include it in the result.

        Args:
            loan_payments (List[LoanPayment]): The list of LoanPayments

        Returns:
            pd.DataFrame: The dataframe with the loan payment data from ipfs
        """

        def trx_state(transaction: str) -> Literal["PAID", "DUE"]:
            # TODO: check XNO RPC to see if the transaction
            #   was made on time, late, or if it's invalid
            if transaction:
                return "PAID"
            else:
                return "DUE"

        data = {'borrower': [], 'lender': [], 'loan': [], 'payment': [], 'amount_due': [], 'due_date': [], 'state': []}
        for payment in loan_payments:
            payment.read()  # read the payment data from ipfs
            data['borrower'].append(payment.borrower_id)
            data['lender'].append(payment.lender_id)
            data['loan'].append(payment.loan_id)
            data['payment'].append(payment.payment_id)
            data['amount_due'].append(payment.reader.amount_due)
            data['due_date'].append(datetime.fromtimestamp(payment.reader.due_date.ToSeconds()))
            data['state'].append(trx_state(payment.reader.transaction))  # check the transaction field to see if they payment was made
        
        # load the data into a pandas dataframe
        return pd.DataFrame.from_dict(data)

    @staticmethod
    def query(borrower_id: UUID, lender_id: UUID, loan_id: UUID) -> Iterator[LoanPayment]:
        """
        Get each loan payment for this loan and read the data from IPFS

        Args:
            borrower_id (UUID): The borrower credit identity
            lender_id (UUID): The lender credit identity
            loan_id (UUID): The loan id

        Returns:
            List[LoanPayment]: The list of LoanPayment objects
        """
        path = f"loan/borrower_{borrower_id}.lender_{lender_id}/loan_{loan_id}"
        # list the loan payments for this loan
        for filename in ipfs.list_files(path):
            if filename:
                # create a LoanPayment object from the filename metadata
                yield LoanPayment.open(f"{path}/{filename}")

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
