# Refunds spec

`refund(order, user_id, amount, now) -> float` refunds part or all of an order.
An `Order` has `owner_id`, `paid`, `refunded` (the total refunded so far) and `placed_at`.

The checks run in this order, and the first one that fails raises its error and changes nothing:

1. Only the order's owner may refund. Anyone else gets `PermissionError`.
2. A refund is allowed up to and including 30 days after `placed_at`. Later gets `ValueError`.
3. The amount must be more than zero. Zero or less gets `ValueError`.
4. The total refunded may never be more than `paid`. A refund that would go over gets `ValueError`.

On success, `order.refunded` grows by `amount`, and the function returns what can still be
refunded: `paid` minus the new `refunded`.
