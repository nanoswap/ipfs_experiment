from __future__ import annotations
import utils
from google.protobuf.message import Message

class File:
    filename: str
    writer: Message
    reader: Message

    def read(self) -> None:
        self.reader.ParseFromString(utils.read(self.filename))

    def write(self) -> None:
        utils.write(self.filename, self.writer.SerializeToString())
    
    def add(self) -> None:
        utils.add(self.filename, self.writer.SerializeToString())

    def delete(self) -> None:
        """ Only needed for local testing """
        utils.delete(self.filename)
