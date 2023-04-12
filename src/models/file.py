from __future__ import annotations
from utils import ipfs
from google.protobuf.message import Message

class IpfsFile:
    filename: str
    writer: Message
    reader: Message

    def read(self) -> None:
        ipfs.read(self.filename, self.reader)

    def write(self) -> None:
        ipfs.write(self.filename, self.writer)
    
    def add(self) -> None:
        ipfs.add(self.filename, self.writer)

    def delete(self) -> None:
        """ Only needed for local testing """
        ipfs.delete(self.filename)
