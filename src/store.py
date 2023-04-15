from __future__ import annotations
from dataclasses import dataclass
from types import FunctionType
from typing import Dict, Iterator, List
from src.ipfs import Ipfs
from google.protobuf.message import Message
from src.index import Index
import errno
import os
import pandas as pd


@dataclass
class Store():
    """
    A utility to read/write protobuf data to ipfs.

    ## Reading:
    ```
        from nanoswap.ipfskvs import Store, Index, Ipfs
        from myprotobuf_pb2 import MyProtobuf

        store = Store(
            Index.from_filename("myfile.txt"),
            ipfs=Ipfs(host="127.0.0.1", port="5001"),
            reader=MyProtobuf()
        )
        store.read()
        print(store.reader)
    ```

    ## Writing:
    ```
        from nanoswap.ipfskvs import Store, Index, Ipfs
        from myprotobuf_pb2 import MyProtobuf

        store = Store(
            Index.from_filename("myfile.txt"),
            ipfs=Ipfs(host="127.0.0.1", port="5001"),
            writer=MyProtobuf()
        )
        store.add()
    ```

    ## Write with multiple indexes
    Create a tiered file structure based on IDs, ex:
    ```
        ├── fashion/
            ├── designer_1.manufacturer_1
            ├── designer_2.manufacturer_1
                ├── deal_16.data
            ├── designer_4.manufacturer_3
                ├── deal_1.data
                ├── deal_2.data
    ```
    ```
        from nanoswap.ipfskvs import Store, Index, Ipfs
        from deal_pb2 import Deal

        index = Index(
            prefix="fashion",
            index={
                "designer": str(uuid.uuid4()),
                "manufacturer": str(uuid.uuid4())
            }, subindex=Index(
                index={
                    "deal":  str(uuid.uuid4())
                }
            )
        )

        data = Deal(type=Type.BUZZ, content="fizz")
        store = Store(index=index, ipfs=Ipfs(), writer=data)
        store.add()
    ```

    ## Query the multiple indexes
    Ex: get all deals with designer id "123"
    ```
        from nanoswap.ipfskvs import Store, Index, Ipfs
        from deal_pb2 import Deal

        query_index = Index(
            prefix="fashion",
            index={
                "designer": "123"
            }
        )
        reader = Deal()
        store = Store.query(query_index, ipfs, reader)
        print(reader)
    ```
    """
    index: Index
    writer: Message
    reader: Message

    def __init__(
            self,
            index: Index,
            ipfs: Ipfs,
            writer: Message = None,
            reader: Message = None) -> None:

        self.index = index
        self.ipfs = ipfs
        self.writer = writer
        self.reader = reader

    def read(self) -> None:
        filename = self.index.get_filename()
        result = self.ipfs.read(filename)
        if not result:
            raise FileNotFoundError(
                errno.ENOENT,
                os.strerror(errno.ENOENT),
                filename
            )

        self.reader.ParseFromString(result)

    def write(self) -> None:
        self.ipfs.write(
            self.index.get_filename(),
            self.writer.SerializeToString()
        )

    def add(self) -> None:
        self.ipfs.add(
            self.index.get_filename(),
            self.writer.SerializeToString()
        )

    def delete(self) -> None:
        """ Only needed for local testing """
        self.ipfs.delete(self.index.get_filename())

    @staticmethod
    def to_dataframe(
            data: List[Store],
            protobuf_parsers: Dict[str, FunctionType]) -> pd.DataFrame:
        """
        Convert a list of Store objects to a pandas dataframe.
        The data for each Store must be read into memory beforehand;
            using `store.read()`

        Args:
            data (List[Store]): The list of Store objects with Indexes
            protobuf_parsers: (Dict[str, function]): key, value pair of
                key (str) --> pandas column name
                value (function) --> how to extract the value from the store

                The function should accept a Store object and return Any

        Returns:
            pd.DataFrame: The index and subindex data
                reformatted into a dataframe
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
        filenames = [file['Name'] for file in response['Entries']]
        for filename in filenames:
            # Listing the same file twice indicates the base case
            #   ex:
            #       path = `ls dir1/dir2` --> filenames = ["filename"]
            #       path = `ls dir1/dir2/filename` --> filenames = ["filename"]
            if filename in path:
                return [query_index]

            # filter filenames based on the index
            full_filename = f"{path}/{filename}".replace("//", "/")
            from_index = Index.from_filename(
                filename=full_filename,
                has_prefix=query_index.prefix
            )
            if query_index.matches(from_index):
                result += Store.query_indexes(from_index, ipfs)

        return result

    @staticmethod
    def query(
            query_index: Index,
            ipfs: Ipfs,
            reader: Message) -> Iterator[Store]:
        for response_index in Store.query_indexes(query_index, ipfs):
            store = Store(index=response_index, reader=reader, ipfs=ipfs)
            store.read()
            yield store
