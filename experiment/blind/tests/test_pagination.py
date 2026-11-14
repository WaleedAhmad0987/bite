import pytest
from experiment.blind.functions.pagination import *


def test_first_page_basic():
    assert page_bounds(100, 1, 10) == (0, 10)


def test_second_page():
    assert page_bounds(100, 2, 10) == (10, 20)


def test_last_full_page():
    assert page_bounds(100, 10, 10) == (90, 100)


def test_partial_last_page():
    assert page_bounds(25, 3, 10) == (20, 25)


def test_page_past_end_returns_empty_range_at_end():
    start, end = page_bounds(25, 10, 10)
    assert start == end == 25


def test_page_just_past_end_exact_multiple():
    assert page_bounds(100, 11, 10) == (100, 100)


def test_page_far_past_end():
    assert page_bounds(5, 1000, 10) == (5, 5)


def test_per_page_capped_at_100():
    assert page_bounds(1000, 1, 500) == (0, 100)


def test_per_page_capped_second_page():
    assert page_bounds(1000, 2, 500) == (100, 200)


def test_per_page_exactly_100():
    assert page_bounds(1000, 1, 100) == (0, 100)


def test_per_page_101_capped():
    assert page_bounds(1000, 1, 101) == (0, 100)


def test_per_page_larger_than_total():
    assert page_bounds(5, 1, 50) == (0, 5)


def test_empty_total_first_page():
    assert page_bounds(0, 1, 10) == (0, 0)


def test_empty_total_later_page():
    assert page_bounds(0, 3, 10) == (0, 0)


def test_per_page_one():
    assert page_bounds(10, 4, 1) == (3, 4)


def test_pages_start_at_1_not_0():
    assert page_bounds(100, 1, 10)[0] == 0


def test_returns_tuple_of_ints():
    result = page_bounds(50, 2, 10)
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert all(isinstance(x, int) for x in result)


def test_start_never_exceeds_end():
    for total in (0, 1, 9, 10, 11, 250):
        for page in (1, 2, 5, 50):
            for per_page in (1, 10, 100, 200):
                start, end = page_bounds(total, page, per_page)
                assert 0 <= start <= end <= total


def test_cap_applied_with_past_end():
    start, end = page_bounds(150, 5, 500)
    assert start == end == 150
