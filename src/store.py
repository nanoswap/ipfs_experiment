from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Iterator, List, Literal
from src import ipfs
from google.protobuf.message import Message
from src.file import File
from src.index import Index
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
    def to_dataframe(data: List[Store], protobuf_parsers: Dict[str, function]) -> pd.DataFrame:
        """
        Convert a list of Store objects to a pandas dataframe.
        This function will read the data for each file, and include it in the result.
        The data for each Store must be read into memory beforehand; using `store.read()`

        Args:
            data (List[Store]): The list of Store objects with Indexes
            protobuf_parsers: (Dict[str, function]): key, value pair of
                key (str) --> pandas column name
                value (function) --> how to extract the value from the store

                The function should accept a Store object and return Any

        Returns:
            pd.DataFrame: The index and subindex data reformatted into a dataframe
        """
        pandas_input = {}
        for store in data:

            # add metadata
            metadata = store.index.get_metadata()
            for key in metadata:
                if key not in pandas_input:
                    pandas_input[key] = []
                
                pandas_input[key].append(metadata[key])

            # add top level data from the reader
            for key in protobuf_parsers:
                if key not in pandas_input:
                    pandas_input[key] = []

                pandas_input[key].append(protobuf_parsers[key](store))

        # load the data into a pandas dataframe
        return pd.DataFrame.from_dict(pandas_input)

    @staticmethod
    def query(index: Index) -> List[Store]:
        path = index.get_filename()

        result = []
        for filename in ipfs.list_files(path):
            has_prefix = index.prefix is not None

            next_index = Index.from_filename(
                f"{path}/{filename}",
                has_prefix = has_prefix
            )

            # check for partial queries
            if index.is_partial() and not index.matches(next_index):
                continue
            
            # Check for subdirectories
            if [filename] == ipfs.list_files(f"{path}/{filename}"):
                # Base case, no subdirectories found
                result.append(Store(index = next_index))

            else:
                result += Store.query(index = next_index)

        return result
