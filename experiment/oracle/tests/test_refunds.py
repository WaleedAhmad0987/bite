import pytest
from datetime import datetime, timedelta

from experiment.oracle.functions.refunds import *


NOW = datetime(2026, 1, 31, 12, 0, 0)


def make_order(owner_id=1, paid=100.0, refunded=0.0, placed_at=None):
    if placed_at is None:
        placed_at = NOW - timedelta(days=1)
    return Order(owner_id=owner_id, paid=paid, refunded=refunded, placed_at=placed_at)


def test_window_constant():
    assert WINDOW == timedelta(days=30)


def test_partial_refund_returns_remaining():
    order = make_order()
    assert refund(order, 1, 40.0, NOW) == 60.0
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
    order = make_order(refunded=60.0)
    assert refund(order, 1, 40.0, NOW) == 0.0


def test_wrong_user_raises_permission_error():
    order = make_order()
    with pytest.raises(PermissionError, match="only the owner"):
        refund(order, 2, 10.0, NOW)
    assert order.refunded == 0.0


def test_permission_checked_before_window():
    order = make_order(placed_at=NOW - timedelta(days=100))
    with pytest.raises(PermissionError):
        refund(order, 2, 10.0, NOW)


def test_permission_checked_before_amount():
    order = make_order()
    with pytest.raises(PermissionError):
        refund(order, 2, -5.0, NOW)


def test_window_closed_raises():
    order = make_order(placed_at=NOW - timedelta(days=31))
    with pytest.raises(ValueError, match="window has closed"):
        refund(order, 1, 10.0, NOW)
    assert order.refunded == 0.0


def test_window_boundary_exactly_30_days_is_closed():
    order = make_order(placed_at=NOW - WINDOW)
    with pytest.raises(ValueError, match="window has closed"):
        refund(order, 1, 10.0, NOW)


def test_window_just_inside_boundary_is_open():
    order = make_order(placed_at=NOW - WINDOW + timedelta(seconds=1))
    assert refund(order, 1, 10.0, NOW) == 90.0


def test_window_checked_before_amount():
    order = make_order(placed_at=NOW - timedelta(days=40))
    with pytest.raises(ValueError, match="window has closed"):
        refund(order, 1, -1.0, NOW)


def test_order_placed_now_is_allowed():
    order = make_order(placed_at=NOW)
    assert refund(order, 1, 10.0, NOW) == 90.0


@pytest.mark.parametrize("amount", [0, 0.0, -1, -0.01])
def test_non_positive_amount_raises(amount):
    order = make_order()
    with pytest.raises(ValueError, match="must be positive"):
        refund(order, 1, amount, NOW)
    assert order.refunded == 0.0


def test_amount_exceeding_paid_raises():
    order = make_order()
    with pytest.raises(ValueError, match="more than was paid"):
        refund(order, 1, 100.01, NOW)
    assert order.refunded == 0.0


def test_amount_exceeding_remaining_raises():
    order = make_order(refunded=70.0)
    with pytest.raises(ValueError, match="more than was paid"):
        refund(order, 1, 30.01, NOW)
    assert order.refunded == 70.0


def test_refund_exact_remaining_succeeds():
    order = make_order(refunded=70.0)
    assert refund(order, 1, 30.0, NOW) == 0.0


def test_fully_refunded_order_rejects_further_refund():
    order = make_order(refunded=100.0)
    with pytest.raises(ValueError, match="more than was paid"):
        refund(order, 1, 0.01, NOW)


def test_failed_refund_does_not_mutate_order():
    order = make_order(refunded=10.0)
    with pytest.raises(ValueError):
        refund(order, 1, 500.0, NOW)
    assert order.refunded == 10.0
    assert order.paid == 100.0


def test_order_dataclass_fields():
    placed = datetime(2026, 1, 1)
    order = Order(owner_id=5, paid=12.5, refunded=2.5, placed_at=placed)
    assert order.owner_id == 5
    assert order.paid == 12.5
    assert order.refunded == 2.5
    assert order.placed_at == placed
