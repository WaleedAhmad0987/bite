from datetime import datetime, timedelta

import pytest

from experiment.strength.functions.refunds import *


NOW = datetime(2026, 11, 14, 12, 0, 0)


def make_order(owner_id=1, paid=100.0, refunded=0.0, placed_at=None):
    if placed_at is None:
        placed_at = NOW - timedelta(days=1)
    return Order(owner_id=owner_id, paid=paid, refunded=refunded, placed_at=placed_at)


def test_window_constant():
    assert WINDOW == timedelta(days=30)


def test_partial_refund_returns_remaining():
    order = make_order()
    assert refund(order, 1, 40.0, NOW) == 60.0


def test_partial_refund_updates_order():
    order = make_order()
    refund(order, 1, 40.0, NOW)
    assert order.refunded == 40.0


def test_full_refund_returns_zero():
    order = make_order()
    assert refund(order, 1, 100.0, NOW) == 0.0
    assert order.refunded == 100.0


def test_multiple_refunds_accumulate():
    order = make_order()
    assert refund(order, 1, 30.0, NOW) == 70.0
    assert refund(order, 1, 20.0, NOW) == 50.0
    assert order.refunded == 50.0


def test_refund_with_existing_refunded_amount():
    order = make_order(refunded=25.0)
    assert refund(order, 1, 25.0, NOW) == 50.0
    assert order.refunded == 50.0


def test_non_owner_raises_permission_error():
    order = make_order()
    with pytest.raises(PermissionError, match="only the owner"):
        refund(order, 2, 10.0, NOW)
    assert order.refunded == 0.0


def test_window_closed_raises():
    order = make_order(placed_at=NOW - timedelta(days=31))
    with pytest.raises(ValueError, match="window has closed"):
        refund(order, 1, 10.0, NOW)
    assert order.refunded == 0.0


def test_exactly_at_window_boundary_allowed():
    order = make_order(placed_at=NOW - timedelta(days=30))
    assert refund(order, 1, 10.0, NOW) == 90.0


def test_just_past_window_boundary_rejected():
    order = make_order(placed_at=NOW - timedelta(days=30, seconds=1))
    with pytest.raises(ValueError, match="window has closed"):
        refund(order, 1, 10.0, NOW)


@pytest.mark.parametrize("amount", [0, 0.0, -1, -0.01])
def test_non_positive_amount_raises(amount):
    order = make_order()
    with pytest.raises(ValueError, match="must be positive"):
        refund(order, 1, amount, NOW)
    assert order.refunded == 0.0


def test_over_refund_raises():
    order = make_order()
    with pytest.raises(ValueError, match="more than was paid"):
        refund(order, 1, 100.01, NOW)
    assert order.refunded == 0.0


def test_over_refund_considering_prior_refunds():
    order = make_order(refunded=80.0)
    with pytest.raises(ValueError, match="more than was paid"):
        refund(order, 1, 20.01, NOW)
    assert order.refunded == 80.0


def test_fully_refunded_order_rejects_any_more():
    order = make_order(refunded=100.0)
    with pytest.raises(ValueError, match="more than was paid"):
        refund(order, 1, 0.01, NOW)


def test_permission_checked_before_window():
    order = make_order(placed_at=NOW - timedelta(days=100))
    with pytest.raises(PermissionError):
        refund(order, 2, 10.0, NOW)


def test_window_checked_before_amount():
    order = make_order(placed_at=NOW - timedelta(days=100))
    with pytest.raises(ValueError, match="window has closed"):
        refund(order, 1, -5.0, NOW)


def test_amount_positive_checked_before_overrefund():
    order = make_order(paid=0.0)
    with pytest.raises(ValueError, match="must be positive"):
        refund(order, 1, 0, NOW)


def test_order_dataclass_fields():
    placed = NOW
    order = Order(owner_id=5, paid=10.0, refunded=1.0, placed_at=placed)
    assert order.owner_id == 5
    assert order.paid == 10.0
    assert order.refunded == 1.0
    assert order.placed_at == placed
