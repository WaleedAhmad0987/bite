import pytest

from experiment.strength.functions.pagination import *


def test_first_page():
    assert page_bounds(100, 1, 10) == (0, 10)


def test_middle_page():
    assert page_bounds(100, 3, 10) == (20, 30)


def test_last_full_page():
    assert page_bounds(100, 10, 10) == (90, 100)


def test_last_partial_page():
    assert page_bounds(25, 3, 10) == (20, 25)


def test_page_beyond_total_returns_total_total():
    assert page_bounds(25, 4, 10) == (25, 25)


def test_page_far_beyond_total():
    assert page_bounds(25, 1000, 10) == (25, 25)


def test_start_exactly_equals_total():
    assert page_bounds(20, 3, 10) == (20, 20)


def test_zero_total():
    assert page_bounds(0, 1, 10) == (0, 0)


def test_negative_total():
    assert page_bounds(-5, 1, 10) == (-5, -5)


def test_per_page_larger_than_total():
    assert page_bounds(5, 1, 10) == (0, 5)


def test_per_page_one():
    assert page_bounds(5, 3, 1) == (2, 3)


def test_per_page_capped_at_max():
    assert page_bounds(1000, 1, 500) == (0, MAX_PER_PAGE)


def test_per_page_cap_affects_offset_of_later_pages():
    assert page_bounds(1000, 2, 500) == (MAX_PER_PAGE, 2 * MAX_PER_PAGE)


def test_per_page_exactly_max():
    assert page_bounds(1000, 2, MAX_PER_PAGE) == (MAX_PER_PAGE, 2 * MAX_PER_PAGE)


def test_per_page_cap_with_partial_last_page():
    assert page_bounds(150, 2, 1000) == (100, 150)


@pytest.mark.parametrize("page", [0, -1, -100])
def test_invalid_page_raises(page):
    with pytest.raises(ValueError):
        page_bounds(100, page, 10)


@pytest.mark.parametrize("per_page", [0, -1, -100])
def test_invalid_per_page_raises(per_page):
    with pytest.raises(ValueError):
        page_bounds(100, 1, per_page)


def test_both_invalid_raises():
    with pytest.raises(ValueError):
        page_bounds(100, 0, 0)


def test_invalid_args_raise_even_when_total_is_zero():
    with pytest.raises(ValueError):
        page_bounds(0, 0, 10)


def test_returns_tuple():
    result = page_bounds(100, 1, 10)
    assert isinstance(result, tuple)
    assert len(result) == 2


def test_max_per_page_constant():
    assert MAX_PER_PAGE == 100
