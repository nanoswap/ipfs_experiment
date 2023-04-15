__package__ = "tests.integration"

import unittest
from src.store import Store
from src.index import Index
from src.ipfs import Ipfs
from protobuf.sample_pb2 import Example, Type
import uuid


class TestPandas(unittest.TestCase):

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

    def sample_data(self):

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
        self.payment_data_2 = Example(type=Type.FIZZ, content="!@#$%^&*()-+_=")
        self.payment_data_3 = Example(type=Type.BUZZ, content="😀😀😀😀😀")
        self.payment_data_4 = Example(type=Type.FIZZ, content="sample text")

        # Create some sample Store objects for testing
        return [
            Store(
                index=TestPandas.generate_index(
                    borrower=self.borrower_1,
                    lender=self.lender,
                    loan=self.loan_1,
                    payment=self.payment_1
                ),
                reader=self.payment_data_1,
                ipfs=Ipfs()
            ),
            Store(
                index=TestPandas.generate_index(
                    borrower=self.borrower_1,
                    lender=self.lender,
                    loan=self.loan_1,
                    payment=self.payment_2
                ),
                reader=self.payment_data_2,
                ipfs=Ipfs()
            ),
            Store(
                index=TestPandas.generate_index(
                    borrower=self.borrower_2,
                    lender=self.lender,
                    loan=self.loan_2,
                    payment=self.payment_3
                ),
                reader=self.payment_data_3,
                ipfs=Ipfs()
            ),
            Store(
                index=TestPandas.generate_index(
                    borrower=self.borrower_2,
                    lender=self.borrower_1,
                    loan=self.loan_3,
                    payment=self.payment_4
                ),
                reader=self.payment_data_4,
                ipfs=Ipfs()
            ),
        ]

    def test_to_dataframe(self):
        sample_data = self.sample_data()
        df = Store.to_dataframe(sample_data, protobuf_parsers={
            "content": lambda store: store.reader.content,
            "type": lambda store: store.reader.type,
        })

        # test column names
        assert df.columns.tolist() == [
            'borrower', 'lender', 'loan', 'payment', 'content', 'type'
        ]

        # test data values
        assert df.iloc[0]['borrower'] == self.borrower_1
        assert df.iloc[0]['lender'] == self.lender
        assert df.iloc[0]['loan'] == self.loan_1
        assert df.iloc[0]['payment'] == self.payment_1
        assert df.iloc[0]['type'] == self.payment_data_1.type
        assert df.iloc[0]['content'] == self.payment_data_1.content

        assert df.iloc[1]['borrower'] == self.borrower_1
        assert df.iloc[1]['lender'] == self.lender
        assert df.iloc[1]['loan'] == self.loan_1
        assert df.iloc[1]['payment'] == self.payment_2
        assert df.iloc[1]['type'] == self.payment_data_2.type
        assert df.iloc[1]['content'] == self.payment_data_2.content

        assert df.iloc[2]['borrower'] == self.borrower_2
        assert df.iloc[2]['lender'] == self.lender
        assert df.iloc[2]['loan'] == self.loan_2
        assert df.iloc[2]['payment'] == self.payment_3
        assert df.iloc[2]['type'] == self.payment_data_3.type
        assert df.iloc[2]['content'] == self.payment_data_3.content

        assert df.iloc[3]['borrower'] == self.borrower_2
        assert df.iloc[3]['lender'] == self.borrower_1
        assert df.iloc[3]['loan'] == self.loan_3
        assert df.iloc[3]['payment'] == self.payment_4
        assert df.iloc[3]['type'] == self.payment_data_4.type
        assert df.iloc[3]['content'] == self.payment_data_4.content
