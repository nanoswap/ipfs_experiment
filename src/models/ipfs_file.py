
import ipfs
from google.protobuf.message import Message

class IpfsFile:
    filename: str
    writer: Message
    reader: Message

    def read(self: object) -> None:
        ipfs.read(self.filename, self.reader)

    def write(self: object) -> None:
        ipfs.write(self.filename, self.writer)
    
    def add(self: object) -> None:
        ipfs.add(self.filename, self.writer)
