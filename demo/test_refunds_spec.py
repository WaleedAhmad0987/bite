from datetime import datetime, timedelta

import pytest

from demo.refunds import *

NOW = datetime(2025, 6, 30, 12, 0, 0)


def make_order(owner_id=1, paid=100.0, refunded=0.0, placed_at=None):
    if placed_at is None:
        placed_at = NOW - timedelta(days=1)
    return Order(owner_id=owner_id, paid=paid, refunded=refunded, placed_at=placed_at)


def snapshot(order):
    return (order.owner_id, order.paid, order.refunded, order.placed_at)


# --- success path ---

def test_partial_refund_returns_remaining():
    order = make_order(paid=100.0, refunded=0.0)
    assert refund(order, 1, 30.0, NOW) == 70.0
    assert order.refunded == 30.0


def test_full_refund_returns_zero():
    order = make_order(paid=100.0)
    assert refund(order, 1, 100.0, NOW) == 0.0
    assert order.refunded == 100.0


def test_refund_accumulates_on_existing_refunded():
    order = make_order(paid=100.0, refunded=40.0)
    assert refund(order, 1, 25.0, NOW) == 35.0
    assert order.refunded == 65.0


def test_successive_refunds():
    order = make_order(paid=100.0)
    assert refund(order, 1, 10.0, NOW) == 90.0
    assert refund(order, 1, 20.0, NOW) == 70.0
    assert order.refunded == 30.0


def test_refund_exactly_remaining_amount_allowed():
    order = make_order(paid=100.0, refunded=60.0)
    assert refund(order, 1, 40.0, NOW) == 0.0
    assert order.refunded == 100.0


def test_small_positive_amount_allowed():
    order = make_order(paid=100.0)
    assert refund(order, 1, 0.01, NOW) == pytest.approx(99.99)
    assert order.refunded == pytest.approx(0.01)


# --- ownership ---

def test_non_owner_raises_permission_error():
    order = make_order(owner_id=1)
    with pytest.raises(PermissionError):
        refund(order, 2, 10.0, NOW)


def test_non_owner_changes_nothing():
    order = make_order(owner_id=1)
    before = snapshot(order)
    with pytest.raises(PermissionError):
        refund(order, 2, 10.0, NOW)
    assert snapshot(order) == before


def test_owner_id_zero_is_respected():
    order = make_order(owner_id=0)
    assert refund(order, 0, 10.0, NOW) == 90.0
    with pytest.raises(PermissionError):
        refund(make_order(owner_id=0), 1, 10.0, NOW)


# --- 30 day window ---

def test_exactly_30_days_allowed():
    order = make_order(placed_at=NOW - timedelta(days=30))
    assert refund(order, 1, 10.0, NOW) == 90.0
    assert order.refunded == 10.0


def test_just_over_30_days_rejected():
    order = make_order(placed_at=NOW - timedelta(days=30, seconds=1))
    with pytest.raises(ValueError):
        refund(order, 1, 10.0, NOW)


def test_just_under_30_days_allowed():
    order = make_order(placed_at=NOW - timedelta(days=30) + timedelta(seconds=1))
    assert refund(order, 1, 10.0, NOW) == 90.0


def test_well_past_30_days_rejected():
    order = make_order(placed_at=NOW - timedelta(days=365))
    with pytest.raises(ValueError):
        refund(order, 1, 10.0, NOW)


def test_expired_changes_nothing():
    order = make_order(placed_at=NOW - timedelta(days=31))
    before = snapshot(order)
    with pytest.raises(ValueError):
        refund(order, 1, 10.0, NOW)
    assert snapshot(order) == before


def test_refund_on_same_moment_as_placed_allowed():
    order = make_order(placed_at=NOW)
    assert refund(order, 1, 10.0, NOW) == 90.0


# --- amount must be positive ---

def test_zero_amount_rejected():
    order = make_order()
    with pytest.raises(ValueError):
        refund(order, 1, 0.0, NOW)


def test_negative_amount_rejected():
    order = make_order()
    with pytest.raises(ValueError):
        refund(order, 1, -5.0, NOW)


def test_invalid_amount_changes_nothing():
    order = make_order(refunded=10.0)
    before = snapshot(order)
    for amt in (0.0, -1.0):
        with pytest.raises(ValueError):
            refund(order, 1, amt, NOW)
    assert snapshot(order) == before


# --- cap at paid ---

def test_over_paid_rejected():
    order = make_order(paid=100.0)
    with pytest.raises(ValueError):
        refund(order, 1, 100.01, NOW)


def test_over_paid_with_existing_refunds_rejected():
    order = make_order(paid=100.0, refunded=60.0)
    with pytest.raises(ValueError):
        refund(order, 1, 40.01, NOW)


def test_fully_refunded_order_rejects_more():
    order = make_order(paid=100.0, refunded=100.0)
    with pytest.raises(ValueError):
        refund(order, 1, 0.01, NOW)


def test_over_cap_changes_nothing():
    order = make_order(paid=100.0, refunded=60.0)
    before = snapshot(order)
    with pytest.raises(ValueError):
        refund(order, 1, 50.0, NOW)
    assert snapshot(order) == before


# --- check ordering ---

def test_permission_checked_before_window():
    order = make_order(owner_id=1, placed_at=NOW - timedelta(days=100))
    with pytest.raises(PermissionError):
        refund(order, 2, 10.0, NOW)


def test_permission_checked_before_amount():
    order = make_order(owner_id=1)
    with pytest.raises(PermissionError):
        refund(order, 2, -5.0, NOW)


def test_permission_checked_before_cap():
    order = make_order(owner_id=1, paid=100.0)
    with pytest.raises(PermissionError):
        refund(order, 2, 500.0, NOW)


def test_window_error_is_value_error_not_permission():
    order = make_order(placed_at=NOW - timedelta(days=100))
    with pytest.raises(ValueError):
        refund(order, 1, -5.0, NOW)
    with pytest.raises(ValueError):
        refund(order, 1, 500.0, NOW)


def test_expired_with_bad_amount_still_unchanged():
    order = make_order(placed_at=NOW - timedelta(days=100), refunded=5.0)
    before = snapshot(order)
    with pytest.raises(ValueError):
        refund(order, 1, 0.0, NOW)
    assert snapshot(order) == before
