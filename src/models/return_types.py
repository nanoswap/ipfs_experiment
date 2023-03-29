from dataclasses import dataclass
from uuid import UUID

import nanoswap.message.lookup_pb2 as lookup_pb2
import nanoswap.message.loan_pb2 as loan_pb2
from enum import Enum

class CreditIdStatus(Enum):
    CREATED = 0
    RETRIEVED = 1

@dataclass
class CreditId:
    id: UUID
    status: CreditIdStatus

            # "borrower": filename.split('.')[0].split("_")[1],
            # "lender": filename.split('.')[1].split("_")[1],
            # "loan": filename.split('.')[2].split("_")[1],
            # "payment": filename.split('.')[3].split("_")[1],
            # "filename": filename

@dataclass
class LoanMetadata:
    borrower: str
    lender: str
    loan: str
    payment: str
    filename: str

@dataclass
class LoanResponse:
    metadata: LoanMetadata
    data: loan_pb2.LoanPayment
