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

    def __init__(self, host: str = "http://localhost", port: int = 5001, version: str = "v0"):
        self.host = host
        self.port = port
        self.version = version

    def _make_request(self, method: str, endpoint: str, params: dict = None, data: dict = None):
        url = f"{self.host}:{self.port}/api/{self.version}/{endpoint}"
        response = requests.request(method, url, params=params, data=json.dumps(data))
        response.raise_for_status()
        return response.json()

    def mkdir(self, directory_name: str) -> None:
        """
        Create a directory in ipfs

        Args:
            directory_name (str): The name of the directory to create
        """
        subprocess.run(["ipfs", "files", "mkdir", directory_name])

    def read(self, filename: str) -> bytes:
        """
        Read a file from ipfs

        Args:
            filename (str): The file to read

        Returns:
            (bytes): The file contents
        """
        # download the data
        result = subprocess.run(["ipfs", "files", "read", f"{IPFS_HOME}/{filename}"], capture_output=True)

        # return the data
        return result.stdout

    def write(self, filename: str, data: bytes) -> None:
        """
        Update an existing file

        Args:
            filename (str): The file to update
            data (Message): The data to overwrite the file with
        """
        # Write data to a local file
        path = f"src/generated/tmp/{filename}"

        # Create the subdirectories locally if they don't already exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            # Serialize the data before writing
            f.write(data)

        # Upload that file
        subprocess.run(["ipfs", "files", "write", "-t", f"{IPFS_HOME}/{filename}", path], capture_output=True)

        # Remove the temporary file
        os.remove(path)

    def add(self, filename: str, data: bytes) -> None:
        """
        Create a new file in ipfs.
        This does not work for updating existing files.

        Args:
            filename (str): The filename for the uploaded data
            data (bytes): The data that will be written to the new file
        """
        # write data to a local file
        path = f"src/generated/tmp/{filename}"
        # create the subdirectories locally if they don't already exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            # serialize the data before writing
            f.write(data)

        # create the directory in ipfs
        directory = "/".join(filename.split("/")[:-1])
        subprocess.run(["ipfs", "files", "mkdir", "-p",f"{IPFS_HOME}/{directory}"])

        # upload that file
        subprocess.run(["ipfs", "add", "-r", path, "--to-files", f"{IPFS_HOME}/{filename}"], capture_output=True)

        # remove the temporary file
        os.remove(path)

    def does_file_exist(self, filename: str) -> bool:
        """
        Check if a file exists in ipfs

        Args:
            filename (str): The file to check

        Returns:
            bool: True if the file exists, false otherwise
        """
        process = subprocess.run(["ipfs", "files", "stat", f"{IPFS_HOME}/{filename}"], capture_output=True)
        does_not_exist = ( process.returncode == 1 and "file does not exist" in process.stderr.decode() )
        return not does_not_exist

    def list_files(self, prefix: str) -> List[str]:
        """
        List the ipfs files in a directory

        Args:
            prefix (str): The path to search on ipfs

        Returns:
            List[str]: The list of filenames found at that location
        """
        process = subprocess.run(["ipfs", "files", "ls", f"{IPFS_HOME}/{prefix}"], capture_output=True)
        files = process.stdout.decode().split("\n")
        return [file for file in files if file]

    def delete(self, filename: str) -> None:
        """
        Delete a file from ipfs

        Args:
            filename (str): The filename to delete
        """
        subprocess.run(["ipfs", "files", "rm", "-r", f"{IPFS_HOME}/{filename}"], capture_output=True)
