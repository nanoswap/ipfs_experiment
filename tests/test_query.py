from faker import Faker
import datetime
import uuid
from src.models.index import Index
from src.models.store import Store
from src.sample_pb2 import Example, Type

Faker.seed(0)
fake = Faker()

def test_query():
   borrower = uuid.uuid4()
   lender = uuid.uuid4()
   loan = uuid.uuid4()

   index = Index(
      prefix="loan",
      index={
         "borrower": borrower,
         "lender": lender
      }, subindex=Index(
         index={
               "loan": loan
         }, subindex=Index(
               index={
                  "payment": uuid.uuid4()
         })
      )
   )

   print(index.get_filename())
   print(Index.from_filename(index.get_filename(), has_prefix=True).get_filename())

   data = Example(type=Type.BUZZ, content="fizz")
   store = Store(index=index, writer=data)
   store.add()
   store2 = Store(index=index, reader=Example())
   store2.read()
   print(store2.reader)

   # query for borrower and lender
   result = list(
      Store.query(
         Index(
            index = {
               "borrower": borrower,
               "lender": lender
            },
            prefix = "loan"
         )
      )
   )
   store3 = result[0]
   print(store3.index.get_filename())

   # query for only a borrower
   result = list(
      Store.query(
         Index(
            index = {
               "borrower": borrower
            },
            prefix = "loan",
            size = 2
         )
      )
   )
   print(result[0].index.get_filename())

   # query for only a lender
   result = list(
      Store.query(
         Index(
            index = {
               "lender": lender
            },
            prefix = "loan",
            size = 2
         )
      )
   )
   print(result[0].index.get_filename())

   # get payments for a loan
   result = list(
      Store.query(
         Index(
            prefix="loan",
            index={
               "borrower": borrower,
               "lender": lender
            }, subindex=Index(
               index={
                     "loan": loan
               }
            )
         )
      )
   )
   print(result[0].index.get_filename())