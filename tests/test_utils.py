from src import utils
from unittest.mock import patch, Mock, MagicMock, call
from google.protobuf.message import Message
import os

def test_mkdir():
    """ Test the `utils.mkdir` function """

    # Define the expected directory name
    directory_name = "test_directory"

    # Define the expected command and output of the subprocess
    expected_command = ["ipfs", "files", "mkdir", directory_name]
    expected_output = b""

    # Patch the subprocess.run() function to return the expected results
    with patch("subprocess.run") as mock_run:
        mock_result = mock_run.return_value
        mock_result.stdout = expected_output

        # Call the mkdir() function with the expected directory name
        utils.mkdir(directory_name)

        # Assert that the subprocess was called with the expected command
        mock_run.assert_called_once_with(expected_command)

def test_read():
    """ Test the `utils.read` function """

    # Create a mock Message object to use in the test
    mock_message = Mock(spec=Message)

    # Define the expected filename and file contents
    filename = "test.txt"
    file_contents = b"This is a test file."

    # Define the expected command and output of the subprocess
    expected_command = ["ipfs", "files", "read", f"{utils.IPFS_HOME}/{filename}"]
    expected_output = file_contents

    # Patch the subprocess.run() function to return the expected output
    with patch("subprocess.run") as mock_run:
        mock_result = Mock()
        mock_result.stdout = expected_output
        mock_run.return_value = mock_result

        # Call the read() function with the mock Message object
        result = utils.read(filename, mock_message)

        # Assert that the subprocess was called with the expected command
        mock_run.assert_called_once_with(expected_command, capture_output=True)

        # Assert that the Message object was called with the expected file contents
        mock_message.ParseFromString.assert_called_once_with(expected_output)

        # Assert that the read() function returned the mock Message object
        assert result == mock_message

def test_write():
    """ Test the `utils.write` function """

    # Define the expected filename and data
    filename = "test.txt"
    file_contents = b"Hello, world!"
    data = MagicMock()
    data.SerializeToString.return_value = file_contents

    # Define the expected commands and outputs of the subprocess calls
    write_command = ["ipfs", "files", "write", "-t", f"{utils.IPFS_HOME}/{filename}", "src/generated/tmp/test.txt"]
    write_output = b""
    rm_command = ["rm", "src/generated/tmp/test.txt"]

    # Patch the subprocess.run() function to return the expected results
    with patch("subprocess.run") as mock_run:
        # Mock the first call to subprocess.run() that writes the file to disk
        mock_write_result = MagicMock()
        mock_write_result.stdout = write_output
        mock_run.side_effect = [mock_write_result, None]

        # Call the write() function with the expected filename and data
        utils.write(filename, data)

        # Assert that subprocess.run() was called twice with the expected commands
        mock_run.assert_has_calls([
            call(write_command, capture_output=True),
            call(rm_command)
        ])

        # Reset the side_effect of the mock_run object
        mock_run.side_effect = None

        # Mock the second call to subprocess.run() that uploads the file to IPFS
        mock_ipfs_result = MagicMock()
        mock_ipfs_result.stdout = write_output
        mock_run.return_value = mock_ipfs_result

        # Call the write() function with the expected filename and data
        utils.write(filename, data)

        # Assert that subprocess.run() was called twice with the expected commands
        mock_run.assert_has_calls([
            call(write_command, capture_output=True),
            call(rm_command),
            call(write_command, capture_output=True),
            call(rm_command),
        ])

def test_add():
    """ Test the `utils.add` function """

    # Mock the data for the protobuf object
    file_contents = b"some contents"
    data = Mock()
    data.SerializeToString.return_value = file_contents


    # Patch the subprocess.run() function to return the expected results
    with patch("subprocess.run") as mock_run:
        # Call the function
        filename = "data/test.txt"
        utils.add(filename, data)

        # Check the calls to subprocess.run
        mock_run.assert_has_calls([
            call(["ipfs", "files", "mkdir", "-p", f"{utils.IPFS_HOME}/data"]),
            call(["ipfs", "add", "-r", f"src/generated/tmp/{filename}", "--to-files", f"{utils.IPFS_HOME}/{filename}"], capture_output=True),
            call(["rm", f"src/generated/tmp/{filename}"])
        ])

def test_does_file_exist():
    """ Test the `utils.does_file_exist` function """

    with patch("subprocess.run") as mock_subprocess:
        # Case where file exists
        mock_subprocess.return_value.stdout.decode.return_value = "NumLinks: 1\nBlockSize: 12\nType: file\n"
        assert utils.does_file_exist("existing_file.txt") == True

        # Check that the correct command is called with the correct argument
        expected_cmd = ["ipfs", "files", "stat", f"{utils.IPFS_HOME}/existing_file.txt"]
        mock_subprocess.assert_called_with(expected_cmd, capture_output=True)

def test_does_file_not_exist():
    """ Test the `utils.does_file_exist` function """

    with patch("subprocess.run") as mock_subprocess:
        # Case where file does not exist
        mock_subprocess.return_value.returncode = 1
        mock_subprocess.return_value.stderr.decode.return_value = "file does not exist"
        assert utils.does_file_exist("non_existing_file.txt") == False

        # Check that the correct command is called with the correct argument
        expected_cmd = ["ipfs", "files", "stat", f"{utils.IPFS_HOME}/non_existing_file.txt"]
        mock_subprocess.assert_called_with(expected_cmd, capture_output=True)

@patch('subprocess.run')
def test_list_files(mock_subprocess: MagicMock):
    # Set up the mock subprocess
    process_mock = MagicMock()
    process_mock.returncode = 0
    process_mock.stdout.decode.return_value = "file1.txt\nfile2.txt\nfile3.txt\n"
    mock_subprocess.return_value = process_mock

    # Test case where files exist
    result = utils.list_files("my_directory")
    assert result == ["file1.txt", "file2.txt", "file3.txt"]

    # Test case where no files exist
    process_mock.stdout.decode.return_value = ""
    result = utils.list_files("empty_directory")
    assert result == []
