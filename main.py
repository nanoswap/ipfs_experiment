import uuid
from src.models.index import Index
from src.models.store import Store
from protobuf.sample_pb2 import Example, Type

class SampleData():

    @staticmethod
    def generate_index(borrower, lender, loan, payment):
        return Index(
            prefix="loan",
            index={
                "borrower": borrower,
                "lender": lender
            }, subindex=Index(
                index={
                    "loan": loan
                }, subindex=Index(
                    index={
                        "payment": payment
                    }
                )
            )
        )

    def __init__(self):

        self.borrower_1 = str(uuid.uuid4())
        self.borrower_2 = str(uuid.uuid4())
        self.lender = str(uuid.uuid4())
        self.loan_1 = str(uuid.uuid4())
        self.loan_2 = str(uuid.uuid4())
        self.loan_3 = str(uuid.uuid4())
        self.payment_1 = str(uuid.uuid4())
        self.payment_2 = str(uuid.uuid4())
        self.payment_3 = str(uuid.uuid4())
        self.payment_4 = str(uuid.uuid4())
        self.payment_data_1 = Example(type=Type.FIZZ, content="lorem")
        self.payment_data_2 = Example(type=Type.FIZZ, content="!@#$%^&*()-+_= ASDFASDFASDF")
        self.payment_data_3 = Example(type=Type.BUZZ, content="😀😀😀😀😀")
        self.payment_data_4 = Example(type=Type.FIZZ, content="sample text")

        # Create some sample Store objects for testing
        self.data = [
            Store(SampleData.generate_index(self.borrower_1, self.lender, self.loan_1, self.payment_1), reader=self.payment_data_1),
            Store(SampleData.generate_index(self.borrower_1, self.lender, self.loan_1, self.payment_2), reader=self.payment_data_2),
            Store(SampleData.generate_index(self.borrower_2, self.lender, self.loan_2, self.payment_3), reader=self.payment_data_3),
            Store(SampleData.generate_index(self.borrower_2, self.borrower_1, self.loan_3, self.payment_4), reader=self.payment_data_4),
        ]

if __name__ == "__main__":
    data = SampleData()
    df = Store.to_dataframe(data.data)
    print(df)
