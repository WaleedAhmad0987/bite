DOMESTIC = "PK"
FREE_OVER_KG = 0.5


def shipping_cost(weight_kg: float, country: str, express: bool = False) -> float:
    if weight_kg <= 0:
        raise ValueError("weight must be positive")
    if country == DOMESTIC and weight_kg < FREE_OVER_KG and not express:
        return 0.0
    base = 5.0 if country == DOMESTIC else 20.0
    cost = base + 2.0 * weight_kg
    if express:
        cost *= 1.5
    return round(cost, 2)
