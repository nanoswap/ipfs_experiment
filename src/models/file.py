from __future__ import annotations
import utils
from google.protobuf.message import Message
import errno
import os

class File:
    writer: Message
    reader: Message

    def read(self) -> None:
        filename = self.index.get_filename()
        result = utils.read(filename)
        if not result:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filename)

        self.reader.ParseFromString(result)

    def write(self) -> None:
        utils.write(self.index.get_filename(), self.writer.SerializeToString())
    
    def add(self) -> None:
        utils.add(self.index.get_filename(), self.writer.SerializeToString())

    def delete(self) -> None:
        """ Only needed for local testing """
        utils.delete(self.index.get_filename())
