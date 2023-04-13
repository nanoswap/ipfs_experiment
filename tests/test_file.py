import unittest
from unittest.mock import patch, MagicMock
from src.file import File

class TestFile(unittest.TestCase):
    @patch('src.ipfs.Ipfs.read')
    def test_read_success(self, mock_read):
        # Arrange
        mock_read.return_value = b'some file contents'
        file = File()
        file.reader = MagicMock()
        file.index = MagicMock()
        file.index.get_filename.return_value = 'testfile'

        # Act
        file.read()

        # Assert
        mock_read.assert_called_once_with('testfile')

    @patch('src.ipfs.Ipfs.read')
    def test_read_failure(self, mock_read):
        # Arrange
        mock_read.return_value = None
        file = File()
        file.reader = MagicMock()
        file.index = MagicMock()
        file.index.get_filename.return_value = 'testfile'

        # Act & Assert
        with self.assertRaises(FileNotFoundError):
            file.read()

    @patch('src.ipfs.Ipfs.write')
    def test_write(self, mock_write):
        # Arrange
        file = File()
        file.index = MagicMock()
        file.index.get_filename.return_value = 'testfile'
        file.writer = MagicMock()
        file.writer.SerializeToString.return_value = b'some data to write'

        # Act
        file.write()

        # Assert
        mock_write.assert_called_once_with('testfile', b'some data to write')

    @patch('src.ipfs.Ipfs.add')
    def test_add(self, mock_add):
        # Arrange
        file = File()
        file.index = MagicMock()
        file.index.get_filename.return_value = 'testfile'
        file.writer = MagicMock()
        file.writer.SerializeToString.return_value = b'some data to write'

        # Act
        file.add()

        # Assert
        mock_add.assert_called_once_with('testfile', b'some data to write')

    @patch('src.ipfs.Ipfs.delete')
    def test_delete(self, mock_delete):
        # Arrange
        file = File()
        file.index = MagicMock()
        file.index.get_filename.return_value = 'testfile'

        # Act
        file.delete()

        # Assert
        mock_delete.assert_called_once_with('testfile')

if __name__ == '__main__':
    unittest.main()
