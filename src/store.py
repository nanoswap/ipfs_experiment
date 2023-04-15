from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Iterator, List, Literal
from src.ipfs import Ipfs
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
        super().__init__()

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
    def query_indexes(query_index: Index, ipfs: Ipfs) -> List[Index]:
        result = []

        # list the files in the directory
        path = query_index.get_filename()
        response = ipfs.list_files(path)
        try:
            filenames = [file['Name'] for file in response['Entries']]
        except KeyError as e:
            if "not a directory" in response["Message"].lower():
                return [query_index]
            else:
                raise e

        for filename in filenames:
            # listing the same file twice indicates the base case
            if filename in path:
                return [query_index]

            # filter filenames based on the index
            full_filename = f"{path}/{filename}".replace("//", "/")
            from_index = Index.from_filename(full_filename, has_prefix = query_index.prefix)
            if query_index.matches(from_index):
                result += Store.query_indexes(from_index, ipfs)

        return result
    
    @staticmethod
    def query(query_index: Index, ipfs: Ipfs, reader: Message) -> Iterator[Store]:
        for response_index in Store.query_indexes(query_index, ipfs):
            store = Store(index=response_index, reader=reader)
            store.read()
            yield store
