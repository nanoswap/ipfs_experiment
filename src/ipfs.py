from dataclasses import dataclass
import subprocess
from typing import List
from google.protobuf.message import Message
import os
import requests
import json
from multicodec import add_prefix, remove_prefix, get_codec
from protobuf.sample_pb2 import Example, Type

IPFS_HOME =  "/data"

@dataclass
class Ipfs():

    def __init__(self, host: str = "http://127.0.0.1", port: int = 5001, version: str = "v0"):
        self.host = host
        self.port = port
        self.version = version

    def _make_request(self, endpoint: str, params: dict = None, files: dict = None, raise_for_status: bool = True):
        url = f"{self.host}:{self.port}/api/{self.version}/{endpoint}"
        response = requests.post(url, params = params, files = files)
        if raise_for_status:
            response.raise_for_status()
        return response.content

    def _dag_put(self, data: bytes) -> str:
        try:
            response = self._make_request(
                endpoint = "dag/put",
                params = {
                    "store-codec": "raw",
                    "input-codec": "raw"
                },
                files = {
                    "object data": add_prefix('raw', data)
                },
                raise_for_status = False
            )
            print(response)
            result = json.loads(response.decode())
            return result["Cid"]["/"]
        except Exception as e:
            print(e)
            raise RuntimeError(e.response._content.decode()) from e

    def _dag_get(self, filename: str) -> str:
        try:
            response = self._make_request(
                endpoint = "dag/get",
                params = {
                    "arg": filename,
                    # "output-codec": "raw"
                },
                raise_for_status = False
            )
            print(response)
            return json.loads(response.decode())
        except Exception as e:
            print(e)
            raise RuntimeError(e.response._content.decode()) from e

    def mkdir(self, directory_name: str, with_home = True) -> None:
        """
        Create a directory in ipfs

        Args:
            directory_name (str): The name of the directory to create
        """
        path = f"{IPFS_HOME}/{directory_name}" if with_home else f"/{directory_name}"
        try:
            self._make_request(
                endpoint = "files/mkdir",
                params = {"arg": path},
                raise_for_status = False
            )
        except Exception as e:
            print(e)
            raise RuntimeError(e.response._content.decode()) from e

    def read(self, filename: str) -> bytes:
        """
        Read a file from ipfs

        Args:
            filename (str): The file to read

        Returns:
            (bytes): The file contents
        """
        try:
            return self._make_request(
                endpoint = "files/read",
                params = {"arg": f"{IPFS_HOME}/{filename}"},
            )
        except Exception as e:
            print(e)
            raise RuntimeError(e.response._content.decode()) from e

    def write(self, filename: str, data: bytes) -> None:
        
        raise NotImplementedError("For now, just use `add` and `delete`")

        try:
            stat = self.stat(filename)
            dag = self._dag_get(stat["Hash"])
            # print(dag)
            # print(dag["/"]["bytes"].encode)
            example = Example()
            example.ParseFromString(dag)
            self._make_request(
                endpoint = "files/write",
                params = {
                    "arg": f"{IPFS_HOME}/{filename}",
                    "truncate": True,
                    "raw-leaves": True
                },
                files = {
                    'file': example.SerializeToString()
                }
            )
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(e.response._content.decode()) from e

    def add(self, filename: str, data: bytes) -> None:
        """
        Create a new file in ipfs.
        This does not work for updating existing files.

        Args:
            filename (str): The filename for the uploaded data
            data (bytes): The data that will be written to the new file
        """
        try:
            self._make_request(
                endpoint = "add",
                params = {
                    "to-files": f"{IPFS_HOME}/{filename}",
                    "raw-leaves": True
                },
                files = {
                    filename: data
                }
            )
        except Exception as e:
            print(e)
            raise RuntimeError(e.response._content.decode()) from e

    def does_file_exist(self, filename: str) -> bool:
        """
        Check if a file exists in ipfs

        Args:
            filename (str): The file to check

        Returns:
            bool: True if the file exists, false otherwise
        """
        try:
            response = self._make_request(
                endpoint = "files/stat",
                params = {"arg": f"{IPFS_HOME}/{filename}"},
                raise_for_status = False
            )
            return 'file does not exist' not in response.decode()
        except Exception as e:
            print(e)
            if 'file does not exist' in e.response._content.decode():
                return False

            raise RuntimeError(e.response._content.decode()) from e

    def stat(self, filename) -> List[str]:
        """
        List the ipfs files in a directory

        Args:
            prefix (str): The path to search on ipfs

        Returns:
            List[str]: The list of filenames found at that location
        """
        try:
            return json.loads(self._make_request(
                endpoint = "files/stat",
                params = {"arg": f"{IPFS_HOME}/{filename}"},
                raise_for_status = False
            ))
        except Exception as e:
            print(e)
            raise RuntimeError(e.response._content.decode()) from e

    def list_files(self, prefix: str = "") -> List[str]:
        """
        List the ipfs files in a directory

        Args:
            prefix (str): The path to search on ipfs

        Returns:
            List[str]: The list of filenames found at that location
        """

        try:
            return json.loads(self._make_request(
                endpoint = "files/ls",
                params = {"arg": f"{IPFS_HOME}/{prefix}"},
                raise_for_status = False
            ))
        except Exception as e:
            print(e)
            raise RuntimeError(e.response._content.decode()) from e
        

    def delete(self, filename: str) -> None:
        """
        Delete a file from ipfs

        Args:
            filename (str): The filename to delete
        """

        try:
            self._make_request(
                endpoint = "files/rm",
                params = {
                    "arg": f"{IPFS_HOME}/{filename}",
                    "recursive": True
                },
                raise_for_status = False
            )
        except Exception as e:
            print(e)
            raise RuntimeError(e.response._content.decode()) from e
