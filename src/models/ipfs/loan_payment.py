
from dataclasses import dataclass
from uuid import UUID
import uuid
import nanoswap.message.loan_pb2 as loan_pb2
from src import ipfs
from google.protobuf.message import Message

class IpfsFile:
    filename: str
    reader: Message
    data: Message

    def read(self: object) -> loan_pb2.LoanPayment:
        """
        Read the data for this object from ipfs

        Args:
            self (object): The metadata to query ipfs

        Returns:
            loan_pb2.LoanPayment: The loan payment object corresponding to the metadata
        """
        self.data = ipfs.read(self.filename, self.reader)

    def write(self: object) -> None:
        """
        Read this file from ipfs and store it in the `data` attribute

        Args:
            self (object): static self
        """
        ipfs.write(self.filename)

@dataclass
class LoanPayment:
    borrower_id: UUID
    lender_id: UUID
    payment_id: UUID
    loan_id: UUID

    def __init__(self: object, borrower_id: UUID, lender_id: UUID, loan_id: UUID) -> None:
        """
        Create a new LoanPayment object

        Args:
            self (object): static LoanPayment
            borrower_id (UUID): The borrower credit identity
            lender_id (UUID): The lender credit identity
            loan_id (UUID): The loan id corresponding to this payment object
        """
        self.reader = loan_pb2.LoanPayment()
        self.borrower_id = borrower_id
        self.lender_id = lender_id
        self.loan_id = loan_id
        self.payment_id = uuid.uuid4()
        self.filename = self.get_filename()

    def __init__(self: object, filename: str) -> None:
        """
        Parse a loan payment filename

        Args:
            self (object): static LoanPaymentMetadata
            filename (str): The filename to parse
        """
        self.reader = loan_pb2.LoanPayment()
        self.filename = filename
        filename_parsed = filename.replace("loan/", "").replace("/", "").split('.')
        self.borrower_id = filename_parsed[0].split("_")[1]
        self.lender_id = filename_parsed[1].split("_")[1]
        self.loan_id = filename_parsed[2].split("_")[1]
        self.payment_id = filename_parsed[3].split("_")[1]

    def get_filename(self: object) -> str:
        """
        Generate the filename for a loan payment

        Args:
            self (object): The `LoanPaymentMetadata` to parse
        Returns:
            str: The filename to use in ipfs
        """
        self.filename = f"loan/borrower_{self.borrower}.lender_{self.lender}/loan_{self.loan_id}/payment_{self.payment_id}"
