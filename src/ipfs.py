from dataclasses import dataclass
import subprocess
from typing import List
from google.protobuf.message import Message
import os
import requests
import json

IPFS_HOME =  "/data"

@dataclass
class Ipfs():

    def __init__(self, host: str = "http://127.0.0.1", port: int = 5001, version: str = "v0"):
        self.host = host
        self.port = port
        self.version = version

    def _make_request(self, method: str, endpoint: str, params: dict = None, data: dict = None, raise_for_status: bool = True):
        url = f"{self.host}:{self.port}/api/{self.version}/{endpoint}"
        response = requests.request(method, url, params = params, files = data)
        if raise_for_status:
            response.raise_for_status()
        return response.content

    def _get_dag(self, filename):
        # need this to pass into files/write
        # https://docs.ipfs.tech/reference/kubo/rpc/#api-v0-dag-get
        pass

    def mkdir(self, directory_name: str, with_home = True) -> None:
        """
        Create a directory in ipfs

        Args:
            directory_name (str): The name of the directory to create
        """
        path = f"{IPFS_HOME}/{directory_name}" if with_home else f"/{directory_name}"
        try:
            self._make_request(
                method = "POST",
                endpoint = "files/mkdir",
                params = {"arg": path},
                raise_for_status = False
            )
        except requests.exceptions.HTTPError as e:
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
                method = "POST",
                endpoint = "files/read",
                params = {"arg": f"{IPFS_HOME}/{filename}"},
            )
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(e.response._content.decode()) from e

    def write(self, filename: str, data: bytes) -> None:
        """
        Update an existing file

        Args:
            filename (str): The file to update
            data (Message): The data to overwrite the file with
        """
        try:
            self._make_request(
                method = "POST",
                endpoint = "files/write",
                params = {
                    "arg": f"{IPFS_HOME}/{filename}",
                    "raw-leaves": True
                },
                data = {
                    "file": data
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
                method = "POST",
                endpoint = "add",
                params = {
                    "to-files": f"{IPFS_HOME}/{filename}",
                    "raw-leaves": True
                },
                data = {
                    filename: data
                }
            )
        except requests.exceptions.HTTPError as e:
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
                method = "POST",
                endpoint = "files/stat",
                params = {"arg": f"{IPFS_HOME}/{filename}"},
                raise_for_status = False
            )
            return 'file does not exist' not in response.decode()
        except requests.exceptions.HTTPError as e:
            if 'file does not exist' in e.response._content.decode():
                return False

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
            # TODO: parse results
            #   b'{"Entries":[{"Name":"Tjupyter_test","Type":0,"Size":0,"Hash":""},{"Name":"identity","Type":0,"Size":0,"Hash":""},{"Name":"jupyter_test","Type":0,"Size":0,"Hash":""},{"Name":"loan","Type":0,"Size":0,"Hash":""},{"Name":"test_directory_2","Type":0,"Size":0,"Hash":""},{"Name":"var","Type":0,"Size":0,"Hash":""}]}\n'
            return self._make_request(
                method = "POST",
                endpoint = "files/ls",
                params = {"arg": f"{IPFS_HOME}/{prefix}"},
                raise_for_status = False
            )
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(e.response._content.decode()) from e
        

    def delete(self, filename: str) -> None:
        """
        Delete a file from ipfs

        Args:
            filename (str): The filename to delete
        """

        try:
            self._make_request(
                method = "POST",
                endpoint = "files/rm",
                params = {
                    "arg": f"{IPFS_HOME}/{filename}",
                    "recursive": True
                },
                raise_for_status = False
            )
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(e.response._content.decode()) from e
