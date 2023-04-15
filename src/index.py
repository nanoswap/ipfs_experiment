from __future__ import annotations
from typing import Dict
from uuid import UUID
import json


class Index():
    prefix: str
    index: Dict[str, UUID]
    size: int  # number of keys in this index (not including parent or subindex)  # noqa: E501
    subindex: Index

    def __init__(
            self,
            index: Dict[str, UUID],
            subindex: Index = None,
            prefix: str = None,
            size: int = None):
        """
            Index keys should be all one word lower case.
            Index values should be UUIDs.
            The prefix should only be on the root/parent index (not in subindex)  # noqa: E501
        """
        self.prefix = prefix
        self.index = index
        self.subindex = subindex
        self.size = size if size else len(index.keys())

    def __str__(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, indent=4)

    def to_dict(self) -> dict:
        return {
            "prefix": self.prefix,
            "index": self.index,
            "subindex": self.subindex.to_dict() if self.subindex else None
        }

    def __eq__(self, other_index: Index) -> bool:
        result = \
            self.prefix == other_index.prefix and \
            self.size == other_index.size and \
            self.subindex == other_index.subindex and \
            self.index == other_index.index
        return result

    def matches(self, other_index: Index) -> bool:
        """
            Check if this index has a compatible index with another index.
            Returns false if any self keys are not in the other index
                or if any values in self are not equal to the
                corresponding value in the other index
        """
        for key in self.index:
            if key not in other_index.index:
                return False

            if str(self.index[key]) != str(other_index.index[key]):
                return False

        return True

    def is_partial(self) -> bool:
        return self.size != len(self.index.keys())

    def get_metadata(self) -> Dict[str, UUID]:
        """ Parse the subindex/filename data """
        filename = self.get_filename()  # recursively get subindex data
        records = filename.split("/")
        if self.prefix:
            records.pop(0)

        result = {}
        for index_level in records:
            for index in index_level.split("."):
                result[index.split("_")[0]] = index.split("_")[1]

        return result

    def get_filename(self) -> str:
        """ Convert this object to a filename """
        result = ""

        # Add prefix
        if self.prefix:
            result += self.prefix + "/"

        # If not all index keys are known, don't add it to the filename
        if self.is_partial():
            return result

        # Add current index
        cur_index = ".".join([
            f'{key}_{value}' for key, value in self.index.items()
        ])
        result += cur_index

        # Recursively add subindexes
        if self.subindex:
            result += "/" + self.subindex.get_filename()

        return result

    @staticmethod
    def from_filename(filename: str, has_prefix: bool = False) -> Index:
        """ Convert a filename to an Index object """
        directories = [file for file in filename.split("/") if file]

        # Get prefix
        prefix = directories.pop(0) if has_prefix else None

        # Get index
        try:
            index = {
                record.split("_")[0]: record.split("_")[1]
                for record in directories.pop(0).split(".")
            }
        except IndexError as e:
            raise Exception(f"Could not parse filename `{filename}` with prefix `{prefix}`") from e  # noqa: E501
        except KeyError as e:
            raise Exception(f"Could not parse filename `{filename}` with prefix `{prefix}`") from e  # noqa: E501

        # Recursively get the subindexes
        subindex = Index.from_filename("/".join(directories)) if len(directories) > 0 else None  # noqa: E501

        return Index(index, subindex, prefix)
