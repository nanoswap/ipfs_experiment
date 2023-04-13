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
    def to_dataframe(data: List[Store], parsed_columns: List[str], parser: function) -> pd.DataFrame:
        """
        Convert a list of Store objects to a pandas dataframe.
        This function will read the data for each file, and include it in the result.

        Args:
            data (List[Store]): The list of Store objects with Indexes

        Returns:
            pd.DataFrame: The index and subindex data reformatted into a dataframe
        """
        pandas_input = {'borrower': [], 'lender': [], 'loan': [], 'payment': [], 'type': [], 'content': []}
        for store in data:

            # add metadata
            metadata = store.index.get_metadata()
            pandas_input['borrower'].append(metadata.get('borrower'))
            pandas_input['lender'].append(metadata.get('lender'))
            pandas_input['loan'].append(metadata.get('loan'))
            pandas_input['payment'].append(metadata.get('payment'))

            # read data, parse it, and add top level data
            # store.read()
            pandas_input['type'].append(store.reader.type)
            pandas_input['content'].append(store.reader.content)

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
