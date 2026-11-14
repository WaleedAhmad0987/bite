from dataclasses import dataclass
from datetime import datetime, timedelta

WINDOW = timedelta(days=30)


@dataclass
class Order:
    owner_id: int
    paid: float
    refunded: float
    placed_at: datetime


def refund(order: Order, user_id: int, amount: float, now: datetime) -> float:
    if user_id != order.owner_id:
        raise PermissionError("only the owner may refund")
    if now - order.placed_at > WINDOW:
        raise ValueError("refund window has closed")
    if amount <= 0:
        raise ValueError("amount must be positive")
    if order.refunded + amount > order.paid:
        raise ValueError("cannot refund more than was paid")
    order.refunded += amount
    return order.paid - order.refunded
