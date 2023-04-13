
from dataclasses import dataclass
from uuid import UUID
import uuid
import datetime
from typing import List
from google.protobuf.timestamp_pb2 import Timestamp
from models.loan_payment import LoanPayment

@dataclass
class Loan:
    borrower_id: UUID
    lender_id: UUID
    loan_id: UUID
    payment_schedule: List[LoanPayment]

    def __init__(
            self: object,
            borrower: UUID,
            lender: UUID,
            amount: int,
            interest: float,
            day_count: int,
            payment_interval_count: int
        ):
        """
        Construct a new loan and write it to ipfs

        Args:
            borrower (str): Credit id of the borrower end-user
            lender (str): Credit id of the lender end-user
            amount (int): Principal amount of the loan (before interest)
            interest (float): Interest of the loan in decimal format (ex: 1.05 is 5%)
            day_count (int): Number of days that the borrower has to finish repaying the loan
            payment_interval_count (int): The number payments that the borrower has to pay
        """
        assert interest > 1

        self.loan_id = uuid.uuid4()
        self.borrower_id = borrower
        self.lender_id = lender

        # create the payment schedule
        self.payment_schedule = []
        self.create_payment_schedule(
            amount,
            interest,
            datetime.timedelta(days=day_count),
            payment_interval_count
        )

    def create_payment_schedule(
            self: object,
            amount: int,
            interest_rate: float,
            total_duration: datetime.timedelta,
            number_of_payments: int
        ):
        """
        Generate a list of loan payment objects based on some initial loan parameters

        Args:
            amount (int): The amount of the loan (before interest)
            interest_rate (float): The interest rate of the loan in decimal (ex: 1.05 is 5%)
            total_duration (datetime.timedelta): The time that the borrower has to finish all repayments
            number_of_payments (int): The number of payments to break up the loan into
        """
        assert interest_rate > 1

        # calculate the payment terms
        total_amount_due = amount * interest_rate
        amount_due_each_payment = int(total_amount_due / number_of_payments)
        first_payment = datetime.datetime.now()

        for payment_interval in range(number_of_payments):
            timestamp = Timestamp()
            timestamp.FromDatetime(first_payment + payment_interval * total_duration)
            # format the data
            loan_payment = LoanPayment(
                borrower_id = self.borrower_id,
                lender_id = self.lender_id,
                loan_id = self.loan_id,
                payment_id = None,
                amount_due = amount_due_each_payment,
                due_date = timestamp
            )
            self.payment_schedule.append(loan_payment)
            # write the data to ipfs
            loan_payment.add()
