import pytest
from experiment.blind.functions.discount import *


def test_save10_applies_ten_percent():
    assert price_after_discount(100, "SAVE10") == pytest.approx(90)


def test_save25_applies_twenty_five_percent():
    assert price_after_discount(100, "SAVE25") == pytest.approx(75)


@pytest.mark.parametrize("code", ["save10", "Save10", "sAvE10", "SAVE10"])
def test_save10_any_case(code):
    assert price_after_discount(100, code) == pytest.approx(90)


@pytest.mark.parametrize("code", ["save25", "Save25", "sAvE25", "SAVE25"])
def test_save25_any_case(code):
    assert price_after_discount(100, code) == pytest.approx(75)


def test_no_code_returns_price_unchanged():
    assert price_after_discount(100, None) == pytest.approx(100)


def test_no_code_under_threshold_unchanged():
    assert price_after_discount(20, None) == pytest.approx(20)


@pytest.mark.parametrize("code", ["SAVE10", "SAVE25"])
def test_under_50_gets_no_discount(code):
    assert price_after_discount(49.99, code) == pytest.approx(49.99)
    assert price_after_discount(10, code) == pytest.approx(10)


def test_zero_price_no_discount():
    assert price_after_discount(0, "SAVE10") == pytest.approx(0)


def test_exactly_50_gets_discount_save10():
    assert price_after_discount(50, "SAVE10") == pytest.approx(45)


def test_exactly_50_gets_discount_save25():
    assert price_after_discount(50, "SAVE25") == pytest.approx(37.5)


def test_discount_capped_at_40_for_save25():
    # 25% of 200 = 50 -> capped at 40
    assert price_after_discount(200, "SAVE25") == pytest.approx(160)


def test_discount_capped_at_40_for_save10():
    # 10% of 1000 = 100 -> capped at 40
    assert price_after_discount(1000, "SAVE10") == pytest.approx(960)


def test_discount_exactly_at_cap_save25():
    # 25% of 160 = 40
    assert price_after_discount(160, "SAVE25") == pytest.approx(120)


def test_discount_just_over_cap_save25():
    assert price_after_discount(180, "SAVE25") == pytest.approx(140)


def test_discount_exactly_at_cap_save10():
    # 10% of 400 = 40
    assert price_after_discount(400, "SAVE10") == pytest.approx(360)


def test_just_below_cap_save10():
    assert price_after_discount(300, "SAVE10") == pytest.approx(270)


def test_negative_price_raises():
    with pytest.raises(Exception):
        price_after_discount(-1, "SAVE10")


def test_negative_price_without_code_raises():
    with pytest.raises(Exception):
        price_after_discount(-5, None)


@pytest.mark.parametrize("code", ["BOGUS", "SAVE15", "SAVE", "", "SAVE10 ", "10SAVE"])
def test_unknown_code_raises(code):
    with pytest.raises(Exception):
        price_after_discount(100, code)


def test_unknown_code_raises_even_under_threshold():
    with pytest.raises(Exception):
        price_after_discount(10, "BOGUS")


def test_returns_numeric():
    result = price_after_discount(100, "SAVE10")
    assert isinstance(result, (int, float))
