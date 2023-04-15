import json
import os
from dataclasses import dataclass
from typing import List, Self

from multicodec import add_prefix

from protobuf.sample_pb2 import Example

import requests


IPFS_HOME = "/data"


@dataclass
class Ipfs():
    """IPFS Python Client.

    This client uses the ipfs rpc via http.
    The ipfs server or gateway is specified in the constructor.

    ### Usage
    For testing with a local ipfs node
    ```py
        import ipfs
        client = ipfs.Ipfs()  # defaults to http://127.0.0.1:5001/api/v0
        client.mkdir("my_dir")
        client.add("my_dir/my_file", b"my_contents")
    ```

    ### References

    IPFS RPC documentation:
        https://docs.ipfs.tech/reference/kubo/rpc/#api-v0-files-write

    For more information about ipfs:
        https://docs.ipfs.tech/concepts/what-is-ipfs/#defining-ipfs
    """
    host: str
    port: int
    version: str

    def __init__(
            self: Self,
            host: str = "http://127.0.0.1",
            port: int = 5001,
            version: str = "v0") -> None:
        """Create an IPFS client.

        Args:
            host (str, optional): IPFS server host or gateway host. Defaults to "http://127.0.0.1".  # noqa: E501
            port (int, optional): IPFS port. Defaults to 5001.
            version (str, optional): IPFS rpc version. Defaults to "v0".
        """
        self.host = host
        self.port = port
        self.version = version

    def _make_request(
            self: Self,
            endpoint: str,
            params: dict = None,
            files: dict = None,
            raise_for_status: bool = True) -> bytes:
        """Make an http request for an IPFS RPC call.

        Args:
            endpoint (str): The IPFS RPC endpoint
            params (dict, optional): The RPC params. Defaults to None.
            files (dict, optional): The RPC files. Defaults to None.
            raise_for_status (bool, optional): If true, raise any
                exceptions that are caught. Defaults to True.

        Returns:
            bytes: The http response data
        """
        url = f"{self.host}:{self.port}/api/{self.version}/{endpoint}"
        response = requests.post(url, params=params, files=files)
        if raise_for_status:
            response.raise_for_status()
        return response.content

    def _dag_put(self: Self, data: bytes) -> str:
        """Call the dag/put endpoint.

        Args:
            data (bytes): The raw object data

        Raises:
            RuntimeError: An exception is raised for any RPC errors

        Returns:
            str: The RPC response
        """
        try:
            response = self._make_request(
                endpoint="dag/put",
                params={
                    "store-codec": "raw",
                    "input-codec": "raw"
                },
                files={
                    "object data": add_prefix('raw', data)
                },
                raise_for_status=False
            )
            result = json.loads(response.decode())
            return result["Cid"]["/"]
        except Exception as e:
            print(e)
            raise RuntimeError(e.response._content.decode()) from e

    def _dag_get(self: Self, filename: str) -> str:
        """Call the dag/get endpoint.

        Args:
            filename (str): The filename to get the dag for

        Raises:
            RuntimeError: An exception is raised for any RPC errors

        Returns:
            str: The RPC response
        """
        try:
            response = self._make_request(
                endpoint="dag/get",
                params={
                    "arg": filename,
                    # "output-codec": "raw"
                },
                raise_for_status=False
            )
            return json.loads(response.decode())
        except Exception as e:
            print(e)
            raise RuntimeError(e.response._content.decode()) from e

    def mkdir(self: Self, directory_name: str, with_home: bool = True) -> None:
        """Create a directory in ipfs.

        Args:
            directory_name (str): The name of the directory to create
            with_home (bool, optional): If true, include Ipfs.IPFS_HOME
                as a directory prefix. Defaults to True.

        Raises:
            RuntimeError: An exception is raised for any RPC errors
        """
        # Split the filename into its directory and basename components
        parts = os.path.split(directory_name)

        # If the directory part is not empty, create it recursively
        if parts[0]:
            self.mkdir(parts[0])

        path = f"{IPFS_HOME}/{directory_name}" if with_home else f"/{directory_name}"  # noqa: E501
        try:
            self._make_request(
                endpoint="files/mkdir",
                params={"arg": path},
                raise_for_status=False
            )
        except Exception as e:
            print(e)
            raise RuntimeError(e.response._content.decode()) from e

    def read(self: Self, filename: str) -> bytes:
        """Read a file from ipfs.

        Args:
            filename (str): The file to read

        Returns:
            (bytes): The file contents
        """
        try:
            return self._make_request(
                endpoint="files/read",
                params={"arg": f"{IPFS_HOME}/{filename}"},
            )
        except Exception as e:
            print(e)
            raise RuntimeError(e.response._content.decode()) from e

    def write(self: Self, filename: str, data: bytes) -> None:
        """Overwrite file contents in ipfs.

        Args:
            filename (str): The filename to write to
            data (bytes): The data to write

        Raises:
            NotImplementedError: This function is not implemented.
                For now, just use `add` and `delete`
        """
        raise NotImplementedError("For now, just use `add` and `delete`")

        try:
            stat = self.stat(filename)
            dag = self._dag_get(stat["Hash"])
            # print(dag)
            # print(dag["/"]["bytes"].encode)
            example = Example()
            example.ParseFromString(dag)
            self._make_request(
                endpoint="files/write",
                params={
                    "arg": f"{IPFS_HOME}/{filename}",
                    "truncate": True,
                    "raw-leaves": True
                },
                files={
                    'file': example.SerializeToString()
                }
            )
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(e.response._content.decode()) from e

    def add(self: Self, filename: str, data: bytes) -> None:
        """Create a new file in ipfs.

        This does not work for updating existing files.

        Args:
            filename (str): The filename for the uploaded data
            data (bytes): The data that will be written to the new file
        """
        # Split the filename into its directory and basename components
        parts = os.path.split(filename)

        # If the directory part is not empty, create it recursively
        if parts[0]:
            self.mkdir(parts[0])

        try:
            self._make_request(
                endpoint="add",
                params={
                    "to-files": f"{IPFS_HOME}/{filename}",
                    "raw-leaves": True
                },
                files={
                    'file': data
                }
            )
        except Exception as e:
            print(e)
            raise RuntimeError(e.response._content.decode()) from e

    def does_file_exist(self: Self, filename: str) -> bool:
        """Check if a file exists in ipfs.

        Args:
            filename (str): The file to check

        Returns:
            bool: True if the file exists, false otherwise
        """
        try:
            response = self._make_request(
                endpoint="files/stat",
                params={"arg": f"{IPFS_HOME}/{filename}"},
                raise_for_status=False
            )
            return 'file does not exist' not in response.decode()
        except Exception as e:
            print(e)
            if 'file does not exist' in e.response._content.decode():
                return False

            raise RuntimeError(e.response._content.decode()) from e

    def stat(self: Self, filename: str) -> bytes:
        """Call the files/stat endpoint.

        Args:
            filename (str): The path to search on ipfs

        Returns:
            bytes: The RPC response
        """
        try:
            return json.loads(self._make_request(
                endpoint="files/stat",
                params={"arg": f"{IPFS_HOME}/{filename}"},
                raise_for_status=False
            ))
        except Exception as e:
            print(e)
            raise RuntimeError(e.response._content.decode()) from e

    def list_files(self: Self, prefix: str = "") -> List[str]:
        """List the ipfs files in a directory.

        Args:
            prefix (str): The path to search on ipfs

        Returns:
            List[str]: The list of filenames found at that location
        """
        try:
            return json.loads(self._make_request(
                endpoint="files/ls",
                params={"arg": f"{IPFS_HOME}/{prefix}"},
                raise_for_status=False
            ))
        except Exception as e:
            print(e)
            raise RuntimeError(e.response._content.decode()) from e

    def delete(self: Self, filename: str) -> None:
        """Delete a file from ipfs.

        Args:
            filename (str): The filename to delete
        """
        try:
            self._make_request(
                endpoint="files/rm",
                params={
                    "arg": f"{IPFS_HOME}/{filename}",
                    "recursive": True
                },
                raise_for_status=False
            )
        except Exception as e:
            print(e)
            raise RuntimeError(e.response._content.decode()) from e
