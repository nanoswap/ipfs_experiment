from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Iterator, List, Literal
import src.utils as utils
from google.protobuf.message import Message
from src.models.file import File
from src.models.index import Index
import pandas as pd


@dataclass
class Store(File):
    index: Index
    writer: Message
    reader: Message

    def __init__(self, index: Index, writer: Message = None, reader: Message = None) -> None:
        self.index = index
        self.writer = writer
        self.reader = reader

    @staticmethod
    def parse_subindex(subindex, result_dict):
        for key, value in subindex.items():
            if isinstance(value, dict):
                Index.parse_subindex(value, result_dict)
            else:
                result_dict[key].append(value)

    @staticmethod
    def to_dataframe(data: List[Store]) -> pd.DataFrame:
        """
        Convert a list of Store objects to a pandas dataframe.
        This function will read the data for each file, and include it in the result.

        Args:
            data (List[Store]): The list of Store objects with Indexes

        Returns:
            pd.DataFrame: The index and subindex data reformatted into a dataframe
        """
        pandas_input = {'borrower': [], 'lender': [], 'loan': [], 'payment': [], 'amount_due': [], 'due_date': [], 'state': []}
        for record in data:
            record.read()  # read the file content from ipfs
            index_data = {}
            Index.parse_subindex(record.index.subindex, index_data)
            print(index_data)
            pandas_input['borrower'].append(index_data.get('borrower'))
            pandas_input['lender'].append(index_data.get('lender'))
            pandas_input['loan'].append(index_data.get('loan'))
            pandas_input['payment'].append(index_data.get('payment'))
            pandas_input['amount_due'].append(index_data.get('amount_due'))
            pandas_input['due_date'].append(index_data.get('due_date'))
            pandas_input['state'].append(index_data.get('state'))
            
        # load the data into a pandas dataframe
        return pd.DataFrame.from_dict(pandas_input)


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
