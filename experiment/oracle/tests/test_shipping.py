import pytest

from experiment.oracle.functions.shipping import *


class TestValidation:
    @pytest.mark.parametrize("weight", [0, -1, -0.5, -100.0])
    def test_non_positive_weight_raises(self, weight):
        with pytest.raises(ValueError, match="weight must be positive"):
            shipping_cost(weight, "PK")

    def test_zero_weight_raises_even_when_express(self):
        with pytest.raises(ValueError):
            shipping_cost(0, "US", express=True)

    def test_invalid_weight_raises_for_international(self):
        with pytest.raises(ValueError):
            shipping_cost(-1, "US")


class TestConstants:
    def test_domestic_constant(self):
        assert DOMESTIC == "PK"

    def test_free_over_kg_constant(self):
        assert FREE_OVER_KG == 0.5


class TestDomesticFree:
    def test_light_domestic_standard_is_free(self):
        assert shipping_cost(0.1, "PK") == 0.0

    def test_just_below_threshold_is_free(self):
        assert shipping_cost(0.49, "PK") == 0.0

    def test_free_returns_float(self):
        assert isinstance(shipping_cost(0.1, "PK"), float)

    def test_at_threshold_is_not_free(self):
        # 0.5 is not < 0.5, so the charge applies: 5 + 2*0.5 = 6.0
        assert shipping_cost(0.5, "PK") == 6.0

    def test_light_domestic_express_is_not_free(self):
        # (5 + 2*0.1) * 1.5 = 7.8
        assert shipping_cost(0.1, "PK", express=True) == 7.8


class TestDomesticPaid:
    def test_above_threshold_standard(self):
        # 5 + 2*1 = 7
        assert shipping_cost(1, "PK") == 7.0

    def test_heavy_standard(self):
        # 5 + 2*10 = 25
        assert shipping_cost(10, "PK") == 25.0

    def test_above_threshold_express(self):
        # (5 + 2*2) * 1.5 = 13.5
        assert shipping_cost(2, "PK", express=True) == 13.5

    def test_at_threshold_express(self):
        # (5 + 1) * 1.5 = 9.0
        assert shipping_cost(0.5, "PK", express=True) == 9.0


class TestInternational:
    def test_light_international_not_free(self):
        # 20 + 2*0.1 = 20.2
        assert shipping_cost(0.1, "US") == 20.2

    def test_international_standard(self):
        # 20 + 2*3 = 26
        assert shipping_cost(3, "US") == 26.0

    def test_international_express(self):
        # (20 + 2*3) * 1.5 = 39
        assert shipping_cost(3, "US", express=True) == 39.0

    def test_unknown_country_uses_international_rate(self):
        assert shipping_cost(1, "ZZ") == 22.0

    def test_country_is_case_sensitive(self):
        # "pk" != "PK", so treated as international
        assert shipping_cost(0.1, "pk") == 20.2

    def test_empty_country_is_international(self):
        assert shipping_cost(1, "") == 22.0


class TestRounding:
    def test_rounds_to_two_decimals(self):
        # 5 + 2*1.234 = 7.468 -> 7.47
        assert shipping_cost(1.234, "PK") == 7.47

    def test_rounds_express_to_two_decimals(self):
        # (20 + 2*1.111) * 1.5 = 33.333 -> 33.33
        assert shipping_cost(1.111, "US", express=True) == 33.33

    def test_result_has_at_most_two_decimals(self):
        result = shipping_cost(2.3333, "US")
        assert result == round(result, 2)

    def test_returns_float_for_paid(self):
        assert isinstance(shipping_cost(1, "PK"), float)


class TestExpressDefault:
    def test_express_defaults_to_false(self):
        assert shipping_cost(0.1, "PK") == shipping_cost(0.1, "PK", express=False)

    def test_express_positional(self):
        assert shipping_cost(1, "US", True) == 33.0

    def test_express_costs_more_than_standard(self):
        assert shipping_cost(1, "US", express=True) > shipping_cost(1, "US")
