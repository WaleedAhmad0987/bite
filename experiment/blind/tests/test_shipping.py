import pytest
from experiment.blind.functions.shipping import *


def test_domestic_light_standard_is_free():
    assert shipping_cost(0.5, "PK") == 0
    assert shipping_cost(0.1, "PK") == 0
    assert shipping_cost(0.5, "PK", express=False) == 0


def test_domestic_light_express_not_free():
    # base 5 + 2*0.5 = 6, express 1.5x = 9
    assert shipping_cost(0.5, "PK", express=True) == pytest.approx(9.0)


def test_domestic_light_express_small_weight():
    # 5 + 2*0.1 = 5.2 -> 7.8
    assert shipping_cost(0.1, "PK", express=True) == pytest.approx(7.8)


def test_domestic_just_over_threshold_standard():
    # 5 + 2*0.51 = 6.02
    assert shipping_cost(0.51, "PK") == pytest.approx(6.02)


def test_domestic_standard_one_kg():
    assert shipping_cost(1, "PK") == pytest.approx(7.0)


def test_domestic_standard_heavy():
    assert shipping_cost(10, "PK") == pytest.approx(25.0)


def test_domestic_express_one_kg():
    assert shipping_cost(1, "PK", express=True) == pytest.approx(10.5)


def test_domestic_express_heavy():
    assert shipping_cost(10, "PK", express=True) == pytest.approx(37.5)


def test_international_standard():
    assert shipping_cost(1, "US") == pytest.approx(22.0)
    assert shipping_cost(5, "GB") == pytest.approx(30.0)


def test_international_express():
    assert shipping_cost(1, "US", express=True) == pytest.approx(33.0)
    assert shipping_cost(5, "GB", express=True) == pytest.approx(45.0)


def test_international_light_parcel_not_free():
    # free rule only applies to domestic
    assert shipping_cost(0.5, "US") == pytest.approx(21.0)
    assert shipping_cost(0.1, "US") == pytest.approx(20.2)
    assert shipping_cost(0.5, "US", express=True) == pytest.approx(31.5)


def test_express_is_1_5x_standard():
    for country in ("PK", "US"):
        std = shipping_cost(3, country)
        exp = shipping_cost(3, country, express=True)
        assert exp == pytest.approx(std * 1.5)


def test_international_costs_more_than_domestic():
    assert shipping_cost(2, "US") > shipping_cost(2, "PK")
    assert shipping_cost(2, "US") - shipping_cost(2, "PK") == pytest.approx(15.0)


def test_cost_increases_with_weight():
    assert shipping_cost(2, "PK") < shipping_cost(3, "PK")
    assert shipping_cost(2, "US") < shipping_cost(3, "US")


def test_returns_number():
    assert isinstance(shipping_cost(1, "PK"), (int, float))
    assert isinstance(shipping_cost(0.2, "PK"), (int, float))


@pytest.mark.parametrize("weight", [0, -1, -0.5, -100])
@pytest.mark.parametrize("country", ["PK", "US"])
@pytest.mark.parametrize("express", [False, True])
def test_non_positive_weight_raises(weight, country, express):
    with pytest.raises(ValueError):
        shipping_cost(weight, country, express)
