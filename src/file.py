from __future__ import annotations
from src.ipfs import Ipfs
from google.protobuf.message import Message
import errno
import os

class File:
    writer: Message
    reader: Message
    ipfs: Ipfs

    def __init__(self) -> None:
        self.ipfs = Ipfs()

    def read(self) -> None:
        filename = self.index.get_filename()
        result = self.ipfs.read(filename)
        if not result:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filename)

        self.reader.ParseFromString(result)

    def write(self) -> None:
        self.ipfs.write(self.index.get_filename(), self.writer.SerializeToString())
    
    def add(self) -> None:
        self.ipfs.add(self.index.get_filename(), self.writer.SerializeToString())

    def delete(self) -> None:
        """ Only needed for local testing """
        self.ipfs.delete(self.index.get_filename())
