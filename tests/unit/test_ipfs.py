__package__ = "tests.unit"

import unittest
from unittest.mock import patch, MagicMock
from src.ipfs import Ipfs
import requests


class TestIpfs(unittest.TestCase):

    @patch('src.ipfs.requests.post')
    def test_mkdir(self, mock_post):
        ipfs = Ipfs()
        mock_post.return_value.raise_for_status.return_value = None
        ipfs.mkdir("test_dir")
        mock_post.assert_called_with(
            "http://127.0.0.1:5001/api/v0/files/mkdir",
            params={"arg": "/data/test_dir"},
            files=None
        )

    @patch('src.ipfs.requests.post')
    def test_read(self, mock_post):
        ipfs = Ipfs()
        mock_post.return_value.content = b"test data"
        result = ipfs.read("test_file")
        mock_post.assert_called_with(
            "http://127.0.0.1:5001/api/v0/files/read",
            params={"arg": "/data/test_file"},
            files=None
        )
        self.assertEqual(result, b"test data")

    @patch('src.ipfs.requests.post')
    def test_add(self, mock_post):
        ipfs = Ipfs()
        mock_post.return_value.raise_for_status.return_value = None
        ipfs.add("test_file", b"test data")
        mock_post.assert_called_with(
            "http://127.0.0.1:5001/api/v0/add",
            params={
                "to-files": "/data/test_file",
                "raw-leaves": True
            },
            files={
                "file": b"test data"
            }
        )

    @patch('src.ipfs.requests.post')
    def test_does_file_exist_true(self, mock_post):
        ipfs = Ipfs()
        mock_post.return_value.content = b"{}"
        result = ipfs.does_file_exist("test_file")
        mock_post.assert_called_with(
            "http://127.0.0.1:5001/api/v0/files/stat",
            params={"arg": "/data/test_file"},
            files=None
        )
        self.assertTrue(result)

    @patch('src.ipfs.requests.post')
    def test_does_file_exist_false(self, mock_post):
        ipfs = Ipfs()
        mock_post.side_effect = requests.exceptions.HTTPError(
            "file does not exist",
            response=MagicMock(
                status_code=404, 
                _content=b'file does not exist'
            )
        )
        result = ipfs.does_file_exist("test_file")
        mock_post.assert_called_with(
            "http://127.0.0.1:5001/api/v0/files/stat",
            params={"arg": "/data/test_file"},
            files=None
        )
        self.assertFalse(result)

    @patch('src.ipfs.requests.post')
    def test_stat(self, mock_post):
        ipfs = Ipfs()
        mock_post.return_value.content = b'{"Type": 2, "CumulativeSize": 0, "Blocks": 0}'  # noqa: E501
        result = ipfs.stat("test_file")
        mock_post.assert_called_with(
            "http://127.0.0.1:5001/api/v0/files/stat",
            params={"arg": "/data/test_file"},
            files=None
        )
        self.assertEqual(result, {"Type": 2, "CumulativeSize": 0, "Blocks": 0})

    @patch('src.ipfs.requests.post')
    def test_delete(self, mock_post):
        ipfs = Ipfs()
        # Call the function
        ipfs.delete("path/to/file.txt")

        # Assert that the correct params were passed to _make_request
        mock_post.assert_called_with(
            "http://127.0.0.1:5001/api/v0/files/rm",
            params={"arg": "/data/path/to/file.txt", "recursive": True},
            files=None
        )
