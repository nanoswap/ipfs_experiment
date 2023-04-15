__package__ = "tests.integration"

import unittest
from faker import Faker
import uuid
from src.index import Index
from src.store import Store
from protobuf.sample_pb2 import Example, Type
from src.ipfs import Ipfs

Faker.seed(0)
fake = Faker()


class TestStore(unittest.TestCase):
    def setUp(self):
        self.borrower = str(uuid.uuid4())
        self.lender = str(uuid.uuid4())
        self.loan = str(uuid.uuid4())

    def test_store_and_read_data(self):
        # create and store example data
        data = Example(type=Type.BUZZ, content="fizz")
        index = Index(
            prefix="loan",
            index={
                "borrower": self.borrower,
                "lender": self.lender
            }, subindex=Index(
                index={
                    "loan": self.loan
                }, subindex=Index(
                    index={
                        "payment": str(uuid.uuid4())
                    }
                )
            )
        )
        store = Store(index=index, writer=data, ipfs=Ipfs())
        store.add()

        # read stored data and check equality
        store2 = Store(index=index, reader=Example(), ipfs=Ipfs())
        store2.read()
        self.assertEqual(store2.reader, data)

    def test_query_borrower_and_lender(self):
        # create and store example data
        data = Example(type=Type.BUZZ, content="fizz")
        index = Index(
            prefix="loan",
            index={
                "borrower": self.borrower,
                "lender": self.lender
            }, subindex=Index(
                index={
                    "loan": self.loan
                }, subindex=Index(
                    index={
                        "payment": str(uuid.uuid4())
                    }
                )
            )
        )
        store = Store(index=index, writer=data, ipfs=Ipfs())
        store.add()

        # query for data by borrower and lender
        query_index = Index(
            index={
                "borrower": self.borrower,
                "lender": self.lender
            },
            prefix="loan"
        )
        results = list(
            Store.query(
                query_index=query_index,
                ipfs=Ipfs(),
                reader=Example()
            )
        )

        # check that the result matches the original data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].index, index)

    def test_query_borrower_only(self):
        # create and store example data
        data = Example(type=Type.BUZZ, content="fizz")
        index = Index(
            prefix="loan",
            index={
                "borrower": self.borrower,
                "lender": self.lender
            }, subindex=Index(
                index={
                    "loan": self.loan
                }, subindex=Index(
                    index={
                        "payment": str(uuid.uuid4())
                    }
                )
            )
        )
        store = Store(index=index, writer=data, ipfs=Ipfs())
        store.add()

        # query for data by borrower only
        query_index = Index(
            index={
                "borrower": self.borrower
            },
            prefix="loan",
            size=2
        )
        results = list(Store.query(query_index, ipfs=Ipfs(), reader=Example()))

        # check that the result matches the original data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].index, index)
