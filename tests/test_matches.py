from typing import Dict
from uuid import UUID
from unittest.mock import Mock

import pytest

from src.index import Index


@pytest.fixture
def index_fixture() -> Index:
    return Index(index={
        'key1': UUID('00000000-0000-0000-0000-000000000001'),
        'key2': UUID('00000000-0000-0000-0000-000000000002'),
        'key3': UUID('00000000-0000-0000-0000-000000000003')
    })


def test_matches_returns_true_when_indexes_are_equal(index_fixture: Index) -> None:
    other_index = Index(index={
        'key1': UUID('00000000-0000-0000-0000-000000000001'),
        'key2': UUID('00000000-0000-0000-0000-000000000002'),
        'key3': UUID('00000000-0000-0000-0000-000000000003')
    })

    assert index_fixture.matches(other_index)


def test_matches_returns_false_when_indexes_are_not_equal(index_fixture: Index) -> None:
    other_index = Index(index={
        'key1': UUID('00000000-0000-0000-0000-000000000001'),
        'key2': UUID('00000000-0000-0000-0000-000000000005'),  # different value
        'key4': UUID('00000000-0000-0000-0000-000000000004')   # different key
    })

    assert not index_fixture.matches(other_index)


def test_matches_returns_false_when_other_index_has_missing_key(index_fixture: Index) -> None:
    other_index = Index(index={
        'key1': UUID('00000000-0000-0000-0000-000000000001'),
        'key2': UUID('00000000-0000-0000-0000-000000000002')
    })

    assert not index_fixture.matches(other_index)
