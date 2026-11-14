import pytest

from experiment.strength.functions.shipping import *


class TestValidation:
    @pytest.mark.parametrize("weight", [0, -1, -0.001, -100.5])
    def test_non_positive_weight_raises(self, weight):
        with pytest.raises(ValueError, match="weight must be positive"):
            shipping_cost(weight, "PK")

    def test_non_positive_weight_raises_international(self):
        with pytest.raises(ValueError):
            shipping_cost(0, "US")

    def test_non_positive_weight_raises_express(self):
        with pytest.raises(ValueError):
            shipping_cost(-1, "PK", express=True)


class TestDomesticFreeShipping:
    def test_free_at_threshold(self):
        assert shipping_cost(0.5, "PK") == 0.0

    def test_free_below_threshold(self):
        assert shipping_cost(0.1, "PK") == 0.0

    def test_free_tiny_weight(self):
        assert shipping_cost(0.0001, "PK") == 0.0

    def test_free_returns_float(self):
        assert isinstance(shipping_cost(0.2, "PK"), float)

    def test_not_free_just_above_threshold(self):
        # 5 + 2 * 0.51 = 6.02
        assert shipping_cost(0.51, "PK") == 6.02

    def test_express_not_free_at_threshold(self):
        # (5 + 2*0.5) * 1.5 = 9.0
        assert shipping_cost(0.5, "PK", express=True) == 9.0

    def test_express_not_free_below_threshold(self):
        # (5 + 2*0.1) * 1.5 = 7.8
        assert shipping_cost(0.1, "PK", express=True) == 7.8


class TestDomesticPaid:
    def test_one_kg(self):
        assert shipping_cost(1, "PK") == 7.0

    def test_ten_kg(self):
        assert shipping_cost(10, "PK") == 25.0

    def test_fractional_weight(self):
        assert shipping_cost(2.5, "PK") == 10.0

    def test_express_one_kg(self):
        # (5 + 2) * 1.5 = 10.5
        assert shipping_cost(1, "PK", express=True) == 10.5

    def test_express_ten_kg(self):
        # (5 + 20) * 1.5 = 37.5
        assert shipping_cost(10, "PK", express=True) == 37.5


class TestInternational:
    def test_one_kg(self):
        assert shipping_cost(1, "US") == 22.0

    def test_small_weight_not_free(self):
        # 20 + 2 * 0.1 = 20.2
        assert shipping_cost(0.1, "US") == 20.2

    def test_at_threshold_not_free(self):
        assert shipping_cost(0.5, "US") == 21.0

    def test_express(self):
        # (20 + 2*1) * 1.5 = 33.0
        assert shipping_cost(1, "US", express=True) == 33.0

    def test_express_small_weight(self):
        # (20 + 0.2) * 1.5 = 30.3
        assert shipping_cost(0.1, "US", express=True) == 30.3

    def test_heavy(self):
        assert shipping_cost(100, "GB") == 220.0

    @pytest.mark.parametrize("country", ["US", "GB", "AE", "IN", ""])
    def test_any_non_domestic_country_uses_international_base(self, country):
        assert shipping_cost(1, country) == 22.0


class TestCountryMatching:
    def test_lowercase_domestic_is_treated_as_international(self):
        assert shipping_cost(1, "pk") == 22.0

    def test_lowercase_domestic_not_free(self):
        assert shipping_cost(0.1, "pk") == 20.2

    def test_whitespace_padded_country_is_international(self):
        assert shipping_cost(1, " PK") == 22.0


class TestRounding:
    def test_rounds_to_two_decimals(self):
        # 5 + 2 * 1.234 = 7.468 -> 7.47
        assert shipping_cost(1.234, "PK") == 7.47

    def test_rounds_express_to_two_decimals(self):
        # (5 + 2 * 1.111) * 1.5 = 10.833 -> 10.83
        assert shipping_cost(1.111, "PK", express=True) == 10.83

    def test_result_has_at_most_two_decimals(self):
        result = shipping_cost(3.14159, "US")
        assert result == round(result, 2)

    def test_returns_float(self):
        assert isinstance(shipping_cost(1, "PK"), float)
        assert isinstance(shipping_cost(1, "US", express=True), float)


class TestConstants:
    def test_domestic_constant(self):
        assert DOMESTIC == "PK"

    def test_free_threshold_constant(self):
        assert FREE_OVER_KG == 0.5


class TestExpressDefault:
    def test_express_defaults_to_false(self):
        assert shipping_cost(1, "PK") == shipping_cost(1, "PK", express=False)

    def test_express_positional(self):
        assert shipping_cost(1, "PK", True) == 10.5

    def test_express_more_expensive_than_standard(self):
        assert shipping_cost(2, "US", express=True) > shipping_cost(2, "US")
