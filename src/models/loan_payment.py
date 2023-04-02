
from dataclasses import dataclass
from typing import List
from uuid import UUID
import uuid
import nanoswap.message.loan_pb2 as loan_pb2
import ipfs
from google.protobuf.message import Message
from google.protobuf.timestamp_pb2 import Timestamp
from models.ipfs_file import IpfsFile
import sys

@dataclass
class LoanPayment(IpfsFile):
    borrower_id: UUID
    lender_id: UUID
    payment_id: UUID
    loan_id: UUID
    filename: str
    writer: Message
    reader: Message = loan_pb2.LoanPayment()

    def __init__(self: object, borrower_id: UUID, lender_id: UUID, loan_id: UUID, amount_due: int = None, due_date: Timestamp = None) -> None:
        self.borrower_id = borrower_id
        self.lender_id = lender_id
        self.loan_id = loan_id
        self.payment_id = uuid.uuid4()

        if amount_due and due_date:
            self.writer = loan_pb2.LoanPayment(amount_due = amount_due, due_date = due_date)
        else:
            self.writer = None

        self.filename = f"loan/borrower_{self.borrower_id}.lender_{self.lender_id}/loan_{self.loan_id}/payment_{self.payment_id}"

    @staticmethod
    def open(filename: str) -> object:
        loan_payment = LoanPayment(
            borrower_id=filename.split("/")[1].split(".")[0].split("_")[1],
            lender_id=filename.split("/")[1].split(".")[1].split("_")[1],
            loan_id=filename.split("/")[2].split("_")[1]
        )
        ipfs.read(filename, loan_payment.reader)
        return loan_payment

    @staticmethod
    def query(borrower_id: UUID, lender_id: UUID, loan_id: UUID) -> List[object]:
        path = f"loan/borrower_{borrower_id}.lender_{lender_id}/loan_{loan_id}"
        result = []
        for filename in ipfs.list_files(path):
            if filename:
                result.append(LoanPayment.open(f"{path}/{filename}"))

        return result

    @staticmethod
    def query_borrower_and_lender(borrower_id: UUID, lender_id: UUID):
        path = f"loan/borrower_{borrower_id}.lender_{lender_id}"
        loans = ipfs.list_files(path)
        result = {}
        for loan in loans:
            
            if not loan:
                continue

            loan_id = loan.split("_")[1]
            loans_payments = LoanPayment.query(borrower_id, lender_id, loan_id)
            result[loan_id] = loans_payments
        
        return result

    @staticmethod
    def query_borrower_or_lender(borrower_id: UUID = None, lender_id: UUID = None):
        assert borrower_id or lender_id

        files = ipfs.list_files(f"loan/")
        result = {}
        for file in files:

            if not file:
                continue

            filename_borrower_id = file.split(".")[0].split("_")[1]
            filename_lender_id = file.split(".")[1].split("_")[1]

            if borrower_id and filename_borrower_id == str(borrower_id):
                result[file] = LoanPayment.query_borrower_and_lender(filename_borrower_id, filename_lender_id)

        
            if lender_id and filename_lender_id == str(lender_id):
                result[file] = LoanPayment.query_borrower_and_lender(filename_borrower_id, filename_lender_id)
        
        return result

    @staticmethod
    def flatten_query_results(loan_payments):
        result = []
        for borrower_lender in loan_payments:
            for loan in loan_payments[borrower_lender]:
                for payment in loan_payments[borrower_lender][loan]:
                    result.append(payment)
        
        return result

    @staticmethod
    def get_earliest_due(loan_payments: List[object]) -> object:
        earliest = sys.maxsize
        result = None
        for payment in loan_payments:
            if payment.reader.due_date.ToSeconds() < earliest:
                earliest = payment.reader.due_date.ToSeconds()
                result = payment
        
        return result
