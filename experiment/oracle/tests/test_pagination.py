import pytest

from experiment.oracle.functions.pagination import *


def test_first_page_basic():
    assert page_bounds(100, 1, 10) == (0, 10)


def test_middle_page():
    assert page_bounds(100, 3, 10) == (20, 30)


def test_last_full_page():
    assert page_bounds(100, 10, 10) == (90, 100)


def test_last_partial_page():
    assert page_bounds(25, 3, 10) == (20, 25)


def test_page_past_end_returns_total_total():
    assert page_bounds(25, 4, 10) == (25, 25)


def test_page_far_past_end():
    assert page_bounds(25, 100, 10) == (25, 25)


def test_start_exactly_at_total():
    assert page_bounds(20, 3, 10) == (20, 20)


def test_empty_total_first_page():
    assert page_bounds(0, 1, 10) == (0, 0)


def test_total_smaller_than_per_page():
    assert page_bounds(5, 1, 10) == (0, 5)


def test_per_page_capped_at_max():
    assert page_bounds(1000, 1, 500) == (0, MAX_PER_PAGE)


def test_per_page_cap_affects_offset_of_later_pages():
    assert page_bounds(1000, 2, 500) == (MAX_PER_PAGE, 2 * MAX_PER_PAGE)


def test_per_page_equal_to_max_not_changed():
    assert page_bounds(1000, 2, MAX_PER_PAGE) == (MAX_PER_PAGE, 2 * MAX_PER_PAGE)


def test_per_page_just_above_max_capped():
    assert page_bounds(1000, 1, MAX_PER_PAGE + 1) == (0, MAX_PER_PAGE)


def test_cap_with_past_end_page():
    assert page_bounds(60, 2, 500) == (50, 60)
    assert page_bounds(60, 3, 500) == (60, 60)


def test_per_page_one():
    assert page_bounds(5, 3, 1) == (2, 3)


def test_max_per_page_value():
    assert MAX_PER_PAGE == 50


@pytest.mark.parametrize("page", [0, -1, -100])
def test_invalid_page_raises(page):
    with pytest.raises(ValueError):
        page_bounds(10, page, 5)


@pytest.mark.parametrize("per_page", [0, -1, -100])
def test_invalid_per_page_raises(per_page):
    with pytest.raises(ValueError):
        page_bounds(10, 1, per_page)


def test_invalid_both_raises():
    with pytest.raises(ValueError):
        page_bounds(10, 0, 0)


def test_validation_precedes_empty_total():
    with pytest.raises(ValueError):
        page_bounds(0, 0, 10)


def test_returns_tuple():
    result = page_bounds(10, 1, 5)
    assert isinstance(result, tuple)
    assert len(result) == 2
