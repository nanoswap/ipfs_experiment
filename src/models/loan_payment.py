
from dataclasses import dataclass
from uuid import UUID
import uuid
import nanoswap.message.loan_pb2 as loan_pb2
import ipfs
from google.protobuf.message import Message
from google.protobuf.timestamp_pb2 import Timestamp

class IpfsFile:
    filename: str
    writer: Message
    reader: Message

    def read(self: object) -> None:
        ipfs.read(self.filename, self.reader)

    def write(self: object) -> None:
        ipfs.write(self.filename, self.writer)
    
    def add(self: object) -> None:
        ipfs.add(self.filename, self.writer)

@dataclass
class LoanPayment(IpfsFile):
    borrower_id: UUID
    lender_id: UUID
    payment_id: UUID
    loan_id: UUID
    filename: str
    writer: Message
    reader: Message = loan_pb2.LoanPayment()

    def __init__(self: object, borrower_id: UUID, lender_id: UUID, loan_id: UUID, amount_due: int, due_date: Timestamp) -> None:
        """
        Create a new LoanPayment object

        Args:
            self (object): static LoanPayment
            borrower_id (UUID): The borrower credit identity
            lender_id (UUID): The lender credit identity
            loan_id (UUID): The loan id corresponding to this payment object
        """
        self.borrower_id = borrower_id
        self.lender_id = lender_id
        self.loan_id = loan_id
        self.payment_id = uuid.uuid4()
        self.writer = loan_pb2.LoanPayment(amount_due = amount_due, due_date = due_date)
        self.filename = f"loan/borrower_{self.borrower_id}.lender_{self.lender_id}/loan_{self.loan_id}/payment_{self.payment_id}"

    # def __init__(self: object, filename: str) -> None:
    #     """
    #     Parse a loan payment filename

    #     Args:
    #         self (object): static LoanPaymentMetadata
    #         filename (str): The filename to parse
    #     """
    #     self.filename = filename
    #     filename_parsed = filename.replace("loan/", "").replace("/", "").split('.')
    #     self.borrower_id = filename_parsed[0].split("_")[1]
    #     self.lender_id = filename_parsed[1].split("_")[1]
    #     self.loan_id = filename_parsed[2].split("_")[1]
    #     self.payment_id = filename_parsed[3].split("_")[1]
