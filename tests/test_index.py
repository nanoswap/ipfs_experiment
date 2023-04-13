import unittest
from unittest.mock import MagicMock, patch
from typing import Dict
from uuid import UUID

from src.models.index import Index

class TestIndex(unittest.TestCase):
    def setUp(self):
        # create a sample index to use in tests
        self.sample_index = {
            "apple": UUID("00000000-0000-0000-0000-000000000001"),
            "banana": UUID("00000000-0000-0000-0000-000000000002"),
            "cherry": UUID("00000000-0000-0000-0000-000000000003"),
        }
    
    def test_init(self):
        # test the initialization of an Index object
        idx = Index(self.sample_index)
        self.assertEqual(idx.index, self.sample_index)
        self.assertIsNone(idx.subindex)
        self.assertIsNone(idx.prefix)
        self.assertEqual(idx.size, len(self.sample_index.keys()))

        sub_index = Index(self.sample_index)
        idx = Index(self.sample_index, sub_index, prefix="test", size=100)
        self.assertEqual(idx.index, self.sample_index)
        self.assertEqual(idx.subindex, sub_index)
        self.assertEqual(idx.prefix, "test")
        self.assertEqual(idx.size, 100)

    def test_is_partial(self):
        # test the is_partial method of an Index object
        idx1 = Index(self.sample_index)
        self.assertFalse(idx1.is_partial())

        idx2 = Index(self.sample_index, size=2)
        self.assertTrue(idx2.is_partial())

    def test_get_filename(self):
        # Test case 1: index with no prefix, no subindex, and all keys known
        idx1 = Index({"a": UUID("00000000-0000-0000-0000-000000000001"), "b": UUID("00000000-0000-0000-0000-000000000002")})
        assert idx1.get_filename() == "a_00000000-0000-0000-0000-000000000001.b_00000000-0000-0000-0000-000000000002"

        # Test case 2: index with a prefix, no subindex, and all keys known
        idx2 = Index({"a": UUID("00000000-0000-0000-0000-000000000001"), "b": UUID("00000000-0000-0000-0000-000000000002")}, prefix="prefix")
        assert idx2.get_filename() == "prefix/a_00000000-0000-0000-0000-000000000001.b_00000000-0000-0000-0000-000000000002"

        # Test case 3: index with a subindex and all keys known
        subindex = Index({"c": UUID("00000000-0000-0000-0000-000000000003")})
        idx3 = Index({"a": UUID("00000000-0000-0000-0000-000000000001"), "b": UUID("00000000-0000-0000-0000-000000000002")}, subindex=subindex)
        assert idx3.get_filename() == "a_00000000-0000-0000-0000-000000000001.b_00000000-0000-0000-0000-000000000002/c_00000000-0000-0000-0000-000000000003"

        # Test case 4: index with unknown key
        idx4 = Index({"a": UUID("00000000-0000-0000-0000-000000000001"), "b": UUID("00000000-0000-0000-0000-000000000002"), "c": UUID("00000000-0000-0000-0000-000000000012")})
        assert idx4.get_filename() == "a_00000000-0000-0000-0000-000000000001.b_00000000-0000-0000-0000-000000000002.c_00000000-0000-0000-0000-000000000012"

        # Test case 5: index with unknown key and subindex
        subindex2 = Index({"d": UUID("00000000-0000-0000-0000-000000000004")})
        idx5 = Index({"a": UUID("00000000-0000-0000-0000-000000000001"), "b": UUID("00000000-0000-0000-0000-000000000002"), "c": UUID("00000000-0000-0000-0000-000000000012")}, subindex=subindex2)
        assert idx5.get_filename() == "a_00000000-0000-0000-0000-000000000001.b_00000000-0000-0000-0000-000000000002.c_00000000-0000-0000-0000-000000000012/d_00000000-0000-0000-0000-000000000004"

    def test_from_filename(self):
        # Test with no subindex
        filename = "baz_12300000-0000-0000-0000-000000000000"
        index = Index.from_filename(filename)
        assert index.prefix == None
        assert index.index == {"baz": "12300000-0000-0000-0000-000000000000"}
        assert index.subindex is None

        # Test with subindex
        filename = "bar/baz_12300000-0000-0000-0000-000000000000/fizz_45600000-0000-0000-0000-000000000000"
        index = Index.from_filename(filename, has_prefix=True)
        assert index.prefix == "bar"
        assert index.index == {"baz": "12300000-0000-0000-0000-000000000000"}
        assert index.subindex.prefix is None
        assert index.subindex.index == {"fizz": "45600000-0000-0000-0000-000000000000"}
        assert index.subindex.subindex is None

        # Test with multiple index
        filename = "foo/a_00000000-0000-0000-0000-000000000001.b_00000000-0000-0000-0000-000000000002"
        index = Index.from_filename(filename, has_prefix=True)
        assert index.prefix == "foo"
        assert index.index == {"a": "00000000-0000-0000-0000-000000000001", "b": "00000000-0000-0000-0000-000000000002"}
        assert index.subindex is None
