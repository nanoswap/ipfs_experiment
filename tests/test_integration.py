from src.ipfs import Ipfs, IPFS_HOME
from unittest.mock import patch, Mock, MagicMock, call, mock_open
from google.protobuf.message import Message
import os

ipfs = Ipfs()

def test_mkdir() -> None:
    """ Test the `utils.mkdir` function """

    # Define the expected directory name
    directory_name = "test_directory"

    # Call the mkdir() function with the expected directory name
    ipfs.mkdir(directory_name)

    # Assert that the subprocess was called with the expected command
    assert ipfs.does_file_exist(directory_name)

    # Cleanup: delete the directory
    ipfs.delete(directory_name)
    