import pytest

from experiment.strength.functions.discount import *


class TestNoDiscountApplied:
    def test_none_code_returns_price_unchanged(self):
        assert price_after_discount(100.0, None) == 100.0

    def test_none_code_below_minimum_returns_price(self):
        assert price_after_discount(10.0, None) == 10.0

    def test_below_min_order_ignores_valid_code(self):
        assert price_after_discount(49.99, "SAVE10") == 49.99

    def test_below_min_order_ignores_unknown_code(self):
        # Minimum-order check happens before code validation
        assert price_after_discount(20.0, "BOGUS") == 20.0

    def test_zero_price_returns_zero(self):
        assert price_after_discount(0, "SAVE10") == 0

    def test_below_min_price_not_rounded(self):
        assert price_after_discount(19.999, "SAVE10") == 19.999


class TestValidCodes:
    def test_save10_applies_ten_percent(self):
        assert price_after_discount(100.0, "SAVE10") == 90.0

    def test_save25_applies_twenty_five_percent(self):
        assert price_after_discount(100.0, "SAVE25") == 75.0

    def test_exactly_min_order_qualifies(self):
        assert price_after_discount(50.0, "SAVE10") == 45.0

    def test_exactly_min_order_save25(self):
        assert price_after_discount(MIN_ORDER, "SAVE25") == 37.5

    def test_code_is_case_insensitive(self):
        assert price_after_discount(100.0, "save10") == 90.0
        assert price_after_discount(100.0, "Save25") == 75.0

    def test_result_is_rounded_to_two_decimals(self):
        # 66.67 * 0.10 = 6.667 -> 60.003 -> 60.0
        assert price_after_discount(66.67, "SAVE10") == 60.0
        # 77.77 * 0.25 = 19.4425 -> 58.3275 -> 58.33
        assert price_after_discount(77.77, "SAVE25") == pytest.approx(58.33)


class TestDiscountCap:
    def test_save25_capped_at_max_discount(self):
        # 25% of 200 = 50 > 40 -> capped
        assert price_after_discount(200.0, "SAVE25") == 160.0

    def test_save10_capped_at_max_discount(self):
        # 10% of 1000 = 100 > 40 -> capped
        assert price_after_discount(1000.0, "SAVE10") == 960.0

    def test_discount_exactly_at_cap(self):
        # 25% of 160 = 40 == cap
        assert price_after_discount(160.0, "SAVE25") == 120.0

    def test_discount_just_under_cap(self):
        # 25% of 100 = 25 < 40
        assert price_after_discount(100.0, "SAVE25") == 75.0

    def test_discount_never_exceeds_max(self):
        price = 5000.0
        result = price_after_discount(price, "SAVE25")
        assert price - result == pytest.approx(MAX_DISCOUNT)


class TestErrors:
    def test_negative_price_raises(self):
        with pytest.raises(ValueError, match="price must not be negative"):
            price_after_discount(-1.0, "SAVE10")

    def test_negative_price_raises_without_code(self):
        with pytest.raises(ValueError, match="price must not be negative"):
            price_after_discount(-0.01, None)

    def test_unknown_code_raises(self):
        with pytest.raises(ValueError, match="unknown code: BOGUS"):
            price_after_discount(100.0, "BOGUS")

    def test_unknown_code_message_preserves_original_case(self):
        with pytest.raises(ValueError, match="unknown code: bogus"):
            price_after_discount(100.0, "bogus")

    def test_empty_code_raises_when_order_qualifies(self):
        with pytest.raises(ValueError, match="unknown code"):
            price_after_discount(100.0, "")

    def test_code_with_whitespace_is_unknown(self):
        with pytest.raises(ValueError, match="unknown code"):
            price_after_discount(100.0, " SAVE10 ")


class TestConstants:
    def test_codes_table(self):
        assert CODES == {"SAVE10": 0.10, "SAVE25": 0.25}

    def test_min_order(self):
        assert MIN_ORDER == 50.0

    def test_max_discount(self):
        assert MAX_DISCOUNT == 40.0
