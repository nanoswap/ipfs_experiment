__package__ = "tests.unit"

from uuid import UUID
import pytest
from src.index import Index


@pytest.fixture
def index_fixture() -> Index:
    return Index(index={
        'key1': UUID('00000000-0000-0000-0000-000000000001'),
        'key2': UUID('00000000-0000-0000-0000-000000000002'),
        'key3': UUID('00000000-0000-0000-0000-000000000003')
    })


def test_matches_returns_true_when_indexes_are_equal(index_fixture: Index):
    other_index = Index(index={
        'key1': UUID('00000000-0000-0000-0000-000000000001'),
        'key2': UUID('00000000-0000-0000-0000-000000000002'),
        'key3': UUID('00000000-0000-0000-0000-000000000003')
    })

    assert index_fixture.matches(other_index)


def test_matches_returns_false_when_indexes_are_not_equal(index_fixture: Index):  # noqa: E501
    other_index = Index(index={
        'key1': UUID('00000000-0000-0000-0000-000000000001'),
        'key2': UUID('00000000-0000-0000-0000-000000000005'),
        'key4': UUID('00000000-0000-0000-0000-000000000004'),
    })

    assert not index_fixture.matches(other_index)


def test_matches_returns_false_when_other_index_has_missing_key(index_fixture: Index):  # noqa: E501
    other_index = Index(index={
        'key1': UUID('00000000-0000-0000-0000-000000000001'),
        'key2': UUID('00000000-0000-0000-0000-000000000002')
    })

    assert not index_fixture.matches(other_index)
