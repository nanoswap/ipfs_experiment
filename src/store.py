from __future__ import annotations

import errno
import os
from dataclasses import dataclass
from types import FunctionType
from typing import Dict, Iterator, List, Self

from google.protobuf.message import Message

import pandas as pd

from src.index import Index
from src.ipfs import Ipfs


@dataclass
class Store():
    """A utility to read/write protobuf data to ipfs.

    Reading:
    ```py
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

    Writing:
    ```py
        from nanoswap.ipfskvs import Store, Index, Ipfs
        from myprotobuf_pb2 import MyProtobuf

        store = Store(
            Index.from_filename("myfile.txt"),
            ipfs=Ipfs(host="127.0.0.1", port="5001"),
            writer=MyProtobuf()
        )
        store.add()
    ```

    Write with multiple indexes.
    Create a tiered file structure based on IDs.
    ```
        ├── fashion/
            ├── designer_1.manufacturer_1
            ├── designer_2.manufacturer_1
                ├── deal_16.data
            ├── designer_4.manufacturer_3
                ├── deal_1.data
                ├── deal_2.data
    ```
    ```py
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

    Query the multiple indexes:
    Ex: get all deals with designer id "123"
    ```py
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
            self: Self,
            index: Index,
            ipfs: Ipfs,
            writer: Message = None,
            reader: Message = None) -> None:
        """Construct a Store object.

        Args:
            index (Index): An object representing the filepath
            ipfs (Ipfs): The IPFS client
            writer (Message, optional): The protobuf object with the
                data to write to ipfs on `.write()`. Defaults to None.
            reader (Message, optional): The protobuf object to populate
                when reading the data from ipfs with `.read()`.
                Defaults to None.
        """
        self.index = index
        self.ipfs = ipfs
        self.writer = writer
        self.reader = reader

    def read(self: Self) -> None:
        """Read the data from ipfs into `self.reader`.

        Raises:
            FileNotFoundError: An exception is raised if the file is
                not found on IPFS.
        """
        filename = self.index.get_filename()
        result = self.ipfs.read(filename)
        if not result:
            raise FileNotFoundError(
                errno.ENOENT,
                os.strerror(errno.ENOENT),
                filename
            )

        self.reader.ParseFromString(result)

    def write(self: Self) -> None:
        """Write the protobuf data from `self.writer` to IPFS."""
        raise NotImplementedError("For now, just use `add` and `delete`")
        self.ipfs.write(
            self.index.get_filename(),
            self.writer.SerializeToString()
        )

    def add(self: Self) -> None:
        """Add the protobuf data from `self.writer` to IPFS."""
        self.ipfs.add(
            self.index.get_filename(),
            self.writer.SerializeToString()
        )

    def delete(self: Self) -> None:
        """Only needed for local testing."""
        self.ipfs.delete(self.index.get_filename())

    @staticmethod
    def to_dataframe(
            data: List[Store],
            protobuf_parsers: Dict[str, FunctionType]) -> pd.DataFrame:
        """Convert a list of Store objects to a pandas dataframe.

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
        """Query ipfs based on the `query_index` param.

        Args:
            query_index (Index): The Index object to use for the query.
            ipfs (Ipfs): The IPFS client.

        Returns:
            List[Index]: The matching filenames found in ipfs, loaded
                into a list of Index objects
        """
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
        """Query ipfs based on the `query_index` param.

        Find the filenames matching the query_index.
        Read the file contents from ipfs for each matching filename.
        Parse the file contents into the reader protobuf object.

        Args:
            query_index (Index): The Index object to use for the query.
            ipfs (Ipfs): The IPFS client.
            reader (Message): _description_

        Yields:
            Iterator[Store]: The list of matching Store objects with
                file content loaded into the `reader` attribute
        """
        for response_index in Store.query_indexes(query_index, ipfs):
            store = Store(index=response_index, reader=reader, ipfs=ipfs)
            store.read()
            yield store
