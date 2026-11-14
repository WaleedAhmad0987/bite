COMMON = {"password123!", "qwerty123456", "letmein12345"}


def is_strong(password: str) -> bool:
    if len(password) <= 12:
        return False
    if password.lower() in COMMON:
        return False
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    return has_upper and has_lower and has_digit
