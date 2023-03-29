from dataclasses import dataclass
from uuid import UUID

import nanoswap.message.loan_pb2 as loan_pb2
from enum import Enum

class CreditIdStatus(Enum):
    CREATED = 0
    RETRIEVED = 1

@dataclass
class CreditId:
    id: UUID
    status: CreditIdStatus

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
