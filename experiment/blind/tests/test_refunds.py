import pytest
from datetime import datetime, timedelta

from experiment.blind.functions.refunds import *

NOW = datetime(2024, 6, 1, 12, 0, 0)


def make_order(owner_id=1, paid=100.0, refunded=0.0, placed_at=None):
    if placed_at is None:
        placed_at = NOW - timedelta(days=5)
    return Order(owner_id=owner_id, paid=paid, refunded=refunded, placed_at=placed_at)


def attempt(order, user_id=1, amount=10.0, now=NOW):
    """Return (result, raised_exception_or_None)."""
    try:
        return refund(order, user_id, amount, now), None
    except Exception as e:
        return None, e


def is_rejected(order, user_id=1, amount=10.0, now=NOW):
    result, exc = attempt(order, user_id, amount, now)
    if exc is not None:
        return True
    # A rejection may also be signalled by returning 0 / falsy
    return not result


# ---------- happy path ----------

def test_owner_valid_refund_returns_amount():
    order = make_order()
    assert refund(order, 1, 10.0, NOW) == 10.0


def test_partial_refund_returns_requested_amount():
    order = make_order(paid=100.0)
    assert refund(order, 1, 25.5, NOW) == 25.5


def test_refund_updates_order_refunded_total():
    order = make_order(paid=100.0, refunded=0.0)
    refund(order, 1, 40.0, NOW)
    assert order.refunded == 40.0


def test_refund_accumulates_on_existing_refunded():
    order = make_order(paid=100.0, refunded=30.0)
    refund(order, 1, 20.0, NOW)
    assert order.refunded == 50.0


def test_multiple_refunds_accumulate():
    order = make_order(paid=100.0)
    refund(order, 1, 30.0, NOW)
    refund(order, 1, 30.0, NOW)
    assert order.refunded == 60.0


# ---------- ownership ----------

def test_non_owner_rejected():
    order = make_order(owner_id=1)
    assert is_rejected(order, user_id=2, amount=10.0)


def test_non_owner_does_not_change_refunded():
    order = make_order(owner_id=1, refunded=5.0)
    attempt(order, user_id=2, amount=10.0)
    assert order.refunded == 5.0


def test_non_owner_rejected_even_for_full_valid_amount():
    order = make_order(owner_id=7, paid=50.0)
    assert is_rejected(order, user_id=8, amount=50.0)


# ---------- time window ----------

def test_refund_exactly_30_days_after_is_allowed():
    order = make_order(placed_at=NOW - timedelta(days=30))
    assert refund(order, 1, 10.0, NOW) == 10.0


def test_refund_one_second_past_30_days_rejected():
    order = make_order(placed_at=NOW - timedelta(days=30, seconds=1))
    assert is_rejected(order)


def test_refund_31_days_rejected():
    order = make_order(placed_at=NOW - timedelta(days=31))
    assert is_rejected(order)


def test_refund_long_after_rejected():
    order = make_order(placed_at=NOW - timedelta(days=365))
    assert is_rejected(order)


def test_refund_just_inside_window_allowed():
    order = make_order(placed_at=NOW - timedelta(days=29, hours=23, minutes=59))
    assert refund(order, 1, 10.0, NOW) == 10.0


def test_refund_same_moment_as_order_allowed():
    order = make_order(placed_at=NOW)
    assert refund(order, 1, 10.0, NOW) == 10.0


def test_rejected_late_refund_does_not_change_refunded():
    order = make_order(placed_at=NOW - timedelta(days=31), refunded=0.0)
    attempt(order)
    assert order.refunded == 0.0


# ---------- amount positivity ----------

def test_zero_amount_rejected():
    order = make_order()
    assert is_rejected(order, amount=0.0)


def test_negative_amount_rejected():
    order = make_order()
    assert is_rejected(order, amount=-5.0)


def test_negative_amount_does_not_change_refunded():
    order = make_order(refunded=10.0)
    attempt(order, amount=-5.0)
    assert order.refunded == 10.0


def test_tiny_positive_amount_allowed():
    order = make_order(paid=100.0)
    assert refund(order, 1, 0.01, NOW) == 0.01


# ---------- cap at total paid ----------

def test_refund_exactly_full_paid_allowed():
    order = make_order(paid=100.0, refunded=0.0)
    assert refund(order, 1, 100.0, NOW) == 100.0


def test_refund_over_paid_rejected():
    order = make_order(paid=100.0, refunded=0.0)
    assert is_rejected(order, amount=100.01)


def test_refund_exceeding_remaining_rejected():
    order = make_order(paid=100.0, refunded=80.0)
    assert is_rejected(order, amount=20.01)


def test_refund_exactly_remaining_allowed():
    order = make_order(paid=100.0, refunded=80.0)
    assert refund(order, 1, 20.0, NOW) == 20.0
    assert order.refunded == 100.0


def test_refund_when_fully_refunded_rejected():
    order = make_order(paid=100.0, refunded=100.0)
    assert is_rejected(order, amount=1.0)


def test_over_cap_rejection_does_not_change_refunded():
    order = make_order(paid=100.0, refunded=80.0)
    attempt(order, amount=50.0)
    assert order.refunded == 80.0


def test_second_refund_beyond_total_rejected():
    order = make_order(paid=100.0)
    refund(order, 1, 60.0, NOW)
    assert is_rejected(order, amount=50.0)
    assert order.refunded == 60.0


def test_zero_paid_order_cannot_be_refunded():
    order = make_order(paid=0.0)
    assert is_rejected(order, amount=1.0)


# ---------- combined conditions ----------

def test_non_owner_and_late_rejected():
    order = make_order(owner_id=1, placed_at=NOW - timedelta(days=60))
    assert is_rejected(order, user_id=2)


def test_owner_late_and_over_cap_rejected():
    order = make_order(placed_at=NOW - timedelta(days=60), paid=10.0)
    assert is_rejected(order, amount=500.0)


def test_owner_id_zero_is_valid_owner():
    order = make_order(owner_id=0)
    assert refund(order, 0, 10.0, NOW) == 10.0
