from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Iterator, List, Literal
import src.utils as utils
from google.protobuf.message import Message
from src.models.file import File
from src.models.index import Index


@dataclass
class Store(File):
    index: Index
    writer: Message
    reader: Message

    def __init__(self, index: Index, writer: Message = None, reader: Message = None) -> None:
        self.index = index
        self.writer = writer
        self.reader = reader
    
    # @staticmethod
    # def to_dataframe(data: List[Store]) -> pd.DataFrame:
    #     """
    #     Convert a list of Store objects to a pandas dataframe.
    #     This function will read the data for each file, and include it in the result.

    #     Args:
    #         data (List[Store]): The list of Store objects

    #     Returns:
    #         pd.DataFrame: The dataframe with the loan payment data from ipfs
    #     """
    #     pandas_input = {'borrower': [], 'lender': [], 'loan': [], 'payment': [], 'amount_due': [], 'due_date': [], 'state': []}
    #     for record in data:
    #         record.read()  # read the file content from ipfs
    #         pandas_input['borrower'].append(payment.borrower_id)
    #         pandas_input['lender'].append(payment.lender_id)
    #         pandas_input['loan'].append(payment.loan_id)
    #         pandas_input['payment'].append(payment.payment_id)
    #         pandas_input['amount_due'].append(payment.reader.amount_due)
    #         pandas_input['due_date'].append(datetime.fromtimestamp(payment.reader.due_date.ToSeconds()))
        
    #     # load the data into a pandas dataframe
    #     return pd.DataFrame.from_dict(pandas_input)

    @staticmethod
    def query(index: Index) -> List[Store]:
        path = index.get_filename()

        result = []
        for filename in utils.list_files(path):
            has_prefix = index.prefix is not None

            next_index = Index.from_filename(
                f"{path}/{filename}",
                has_prefix = has_prefix
            )

            # check for partial queries
            if index.is_partial() and not index.matches(next_index):
                continue
            
            # Check for subdirectories
            if [filename] == utils.list_files(f"{path}/{filename}"):
                # Base case, no subdirectories found
                result.append(Store(index = next_index))

            else:
                result += Store.query(index = next_index)

        return result
