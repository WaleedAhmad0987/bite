import pytest

from experiment.oracle.functions.discount import *


class TestNoDiscountPaths:
    def test_no_code_returns_price_unchanged(self):
        assert price_after_discount(100.0, None) == 100.0

    def test_no_code_below_minimum_returns_price_unchanged(self):
        assert price_after_discount(10.0, None) == 10.0

    def test_below_minimum_with_valid_code_returns_price_unchanged(self):
        assert price_after_discount(49.99, "SAVE10") == 49.99

    def test_below_minimum_with_unknown_code_does_not_raise(self):
        assert price_after_discount(20.0, "BOGUS") == 20.0

    def test_zero_price_with_code(self):
        assert price_after_discount(0, "SAVE10") == 0

    def test_zero_price_no_code(self):
        assert price_after_discount(0.0, None) == 0.0


class TestValidation:
    def test_negative_price_raises(self):
        with pytest.raises(ValueError, match="price must not be negative"):
            price_after_discount(-1.0, None)

    def test_negative_price_raises_even_with_code(self):
        with pytest.raises(ValueError, match="price must not be negative"):
            price_after_discount(-100.0, "SAVE10")

    def test_unknown_code_at_or_above_minimum_raises(self):
        with pytest.raises(ValueError, match="unknown code: BOGUS"):
            price_after_discount(100.0, "BOGUS")

    def test_unknown_code_exactly_at_minimum_raises(self):
        with pytest.raises(ValueError, match="unknown code"):
            price_after_discount(50.0, "NOPE")

    def test_empty_string_code_is_unknown(self):
        with pytest.raises(ValueError, match="unknown code"):
            price_after_discount(100.0, "")

    def test_code_is_case_sensitive(self):
        with pytest.raises(ValueError, match="unknown code"):
            price_after_discount(100.0, "save10")


class TestDiscountCalculation:
    def test_save10_at_minimum_boundary(self):
        assert price_after_discount(50.0, "SAVE10") == 45.0

    def test_save25_at_minimum_boundary(self):
        assert price_after_discount(50.0, "SAVE25") == 37.5

    def test_save10_typical(self):
        assert price_after_discount(200.0, "SAVE10") == 180.0

    def test_save25_typical(self):
        assert price_after_discount(100.0, "SAVE25") == 75.0

    def test_result_is_rounded_to_two_decimals(self):
        # 99.99 * 0.10 = 9.999 -> 89.991 -> 89.99
        assert price_after_discount(99.99, "SAVE10") == 89.99

    def test_rounding_of_fractional_result(self):
        # 50.55 - 5.055 = 45.495 -> rounds to 2 decimals
        result = price_after_discount(50.55, "SAVE10")
        assert result == round(50.55 - 50.55 * 0.10, 2)

    def test_integer_price_accepted(self):
        assert price_after_discount(100, "SAVE10") == 90.0


class TestMaxDiscountCap:
    def test_save10_cap_not_reached_at_399(self):
        # 10% of 399 = 39.9 < 40
        assert price_after_discount(399.0, "SAVE10") == pytest.approx(359.1)

    def test_save10_cap_reached_at_400(self):
        # 10% of 400 = 40 == cap
        assert price_after_discount(400.0, "SAVE10") == 360.0

    def test_save10_capped_above_400(self):
        assert price_after_discount(1000.0, "SAVE10") == 960.0

    def test_save25_cap_reached_at_160(self):
        # 25% of 160 = 40 == cap
        assert price_after_discount(160.0, "SAVE25") == 120.0

    def test_save25_capped_above_160(self):
        assert price_after_discount(400.0, "SAVE25") == 360.0

    def test_save25_below_cap(self):
        assert price_after_discount(120.0, "SAVE25") == 90.0

    def test_huge_price_discount_is_max(self):
        assert price_after_discount(1_000_000.0, "SAVE25") == 1_000_000.0 - 40.0


class TestConstants:
    def test_constants(self):
        assert CODES == {"SAVE10": 0.10, "SAVE25": 0.25}
        assert MIN_ORDER == 50.0
        assert MAX_DISCOUNT == 40.0

    @pytest.mark.parametrize("code", ["SAVE10", "SAVE25"])
    def test_discounted_price_never_exceeds_original(self, code):
        for price in (50.0, 75.5, 160.0, 500.0):
            assert price_after_discount(price, code) < price

    @pytest.mark.parametrize("code", ["SAVE10", "SAVE25"])
    def test_discount_never_exceeds_cap(self, code):
        for price in (50.0, 500.0, 5000.0):
            assert price - price_after_discount(price, code) <= MAX_DISCOUNT + 0.01
