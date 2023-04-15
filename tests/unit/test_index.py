__package__ = "tests.unit"

import unittest
from uuid import UUID
from src.index import Index


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

    def test_get_filename_no_prefix_no_subindex(self):
        # Test case 1: index with no prefix, no subindex
        idx1 = Index(
            index={
                "a": UUID("00000000-0000-0000-0000-000000000001"),
                "b": UUID("00000000-0000-0000-0000-000000000002")
            }
        )
        assert idx1.get_filename() == "a_00000000-0000-0000-0000-000000000001.b_00000000-0000-0000-0000-000000000002"  # noqa: E501

    def test_get_filename_with_prefix_no_subindex(self):
        # Test case 2: index with a prefix, no subindex
        idx2 = Index(
            index={
                "a": UUID("00000000-0000-0000-0000-000000000001"),
                "b": UUID("00000000-0000-0000-0000-000000000002")
            },
            prefix="prefix"
        )
        assert idx2.get_filename() == "prefix/a_00000000-0000-0000-0000-000000000001.b_00000000-0000-0000-0000-000000000002"  # noqa: E501

    def test_get_filename_with_subindex(self):
        # Test case 3: index with a subindex
        idx3 = Index(
            index={
                "a": UUID("00000000-0000-0000-0000-000000000001"),
                "b": UUID("00000000-0000-0000-0000-000000000002")
            },
            subindex=Index(
                index={
                    "c": UUID("00000000-0000-0000-0000-000000000003")
                }
            )
        )
        assert idx3.get_filename() == "a_00000000-0000-0000-0000-000000000001.b_00000000-0000-0000-0000-000000000002/c_00000000-0000-0000-0000-000000000003"  # noqa: E501

    def test_get_filename_multiple_index_no_subindex(self):
        # Test case 4: index with multiple indexes, no subindex
        idx4 = Index(
            index={
                "a": UUID("00000000-0000-0000-0000-000000000001"),
                "b": UUID("00000000-0000-0000-0000-000000000002"),
                "c": UUID("00000000-0000-0000-0000-000000000012")
            }
        )
        assert idx4.get_filename() == "a_00000000-0000-0000-0000-000000000001.b_00000000-0000-0000-0000-000000000002.c_00000000-0000-0000-0000-000000000012"  # noqa: E501

    def test_get_filename_multiple_index_with_subindex(self):
        # Test case 5: index with multiple indexes and subindex
        idx5 = Index(
            index={
                "a": UUID("00000000-0000-0000-0000-000000000001"),
                "b": UUID("00000000-0000-0000-0000-000000000002"),
                "c": UUID("00000000-0000-0000-0000-000000000012")
            },
            subindex=Index(
                {
                    "d": UUID("00000000-0000-0000-0000-000000000004")
                }
            )
        )
        assert idx5.get_filename() == "a_00000000-0000-0000-0000-000000000001.b_00000000-0000-0000-0000-000000000002.c_00000000-0000-0000-0000-000000000012/d_00000000-0000-0000-0000-000000000004"  # noqa: E501

    def test_from_filename_no_subindex(self):
        # Test with no subindex
        filename = "baz_12300000-0000-0000-0000-000000000000"
        index = Index.from_filename(filename)
        assert index.prefix is None
        assert index.index == {"baz": "12300000-0000-0000-0000-000000000000"}
        assert index.subindex is None

    def test_from_filename_with_subindex(self):
        # Test with subindex
        filename = "bar/baz_12300000-0000-0000-0000-000000000000/fizz_45600000-0000-0000-0000-000000000000"  # noqa: E501
        index = Index.from_filename(filename, has_prefix=True)
        assert index.prefix == "bar"
        assert index.index == {"baz": "12300000-0000-0000-0000-000000000000"}
        assert index.subindex.prefix is None
        assert index.subindex.index == {"fizz": "45600000-0000-0000-0000-000000000000"}  # noqa: E501
        assert index.subindex.subindex is None

    def test_from_filename_multiple_index(self):
        # Test with multiple index
        filename = "foo/a_00000000-0000-0000-0000-000000000001.b_00000000-0000-0000-0000-000000000002"  # noqa: E501
        index = Index.from_filename(filename, has_prefix=True)
        assert index.prefix == "foo"
        assert index.index == {"a": "00000000-0000-0000-0000-000000000001", "b": "00000000-0000-0000-0000-000000000002"}  # noqa: E501
        assert index.subindex is None
