from __future__ import annotations
from typing import Dict
from uuid import UUID

class Index():
    prefix: str
    index: Dict[str, UUID]
    subindex: Index

    def __init__(self, index: Dict[str, UUID], subindex: Index = None, prefix: str = None):
        """
            Index keys should be all one word lower case.
            Index values should be UUIDs.
            The prefix should only be on the root/parent index (not in subindex)
        """
        self.prefix = prefix
        self.index = index
        self.subindex = subindex

    def get_filename(self) -> str:
        """ Convert this object to a filename """
        result = ""

        # Add prefix
        if self.prefix:
            result += self.prefix + "/"

        # Add current index
        cur_index = ".".join([f'{key}_{value}' for key, value in self.index.items()])
        result += cur_index

        # Recursively add subindexes
        if self.subindex:
            result += "/" + self.subindex.get_filename()

        return result

    @staticmethod
    def from_filename(filename: str, has_prefix: bool = False) -> Index:
        """ Convert a filename to an Index object """
        directories = filename.split("/")

        # Get prefix
        prefix = directories.pop(0) if has_prefix else None
        
        # Get index
        index = {
            record.split("_")[0]: record.split("_")[1]
            for record in directories.pop(0).split(".")
        }

        # Recursively get the subindexes
        subindex = Index.from_filename("/".join(directories)) if len(directories) > 0 else None

        return Index(index, subindex, prefix)
