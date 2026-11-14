CODES = {"SAVE10": 0.10, "SAVE25": 0.25}
MIN_ORDER = 50.0
MAX_DISCOUNT = 40.0


def price_after_discount(price: float, code: str | None) -> float:
    if price < 0:
        raise ValueError("price must not be negative")
    if code is None or price < MIN_ORDER:
        return price
    rate = CODES.get(code)
    if rate is None:
        raise ValueError(f"unknown code: {code}")
    discount = min(price * rate, MAX_DISCOUNT)
    return round(price - discount, 2)
