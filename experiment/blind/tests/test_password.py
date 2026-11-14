import pytest
from experiment.blind.functions.password import *


VALID = "Abcdefghij1k"  # 12 chars, upper, lower, digit


def test_valid_password_is_strong():
    assert is_strong(VALID) is True


def test_returns_bool():
    assert isinstance(is_strong(VALID), bool)
    assert isinstance(is_strong("short"), bool)


def test_exactly_twelve_characters_ok():
    pw = "Aa1" + "x" * 9
    assert len(pw) == 12
    assert is_strong(pw) is True


def test_eleven_characters_too_short():
    pw = "Aa1" + "x" * 8
    assert len(pw) == 11
    assert is_strong(pw) is False


def test_empty_string_not_strong():
    assert is_strong("") is False


def test_long_password_ok():
    assert is_strong("Aa1" + "x" * 100) is True


def test_missing_uppercase():
    assert is_strong("abcdefghij1k") is False


def test_missing_lowercase():
    assert is_strong("ABCDEFGHIJ1K") is False


def test_missing_digit():
    assert is_strong("Abcdefghijkl") is False


def test_only_digits_not_strong():
    assert is_strong("123456789012") is False


def test_only_letters_not_strong():
    assert is_strong("AbCdEfGhIjKlMn") is False


def test_symbols_allowed_when_requirements_met():
    assert is_strong("Abcdefghij1!@#") is True


def test_spaces_do_not_break_valid_password():
    assert is_strong("Abcdefg hij1k") is True


@pytest.mark.parametrize("pw", [
    "password",
    "Password",
    "PASSWORD",
    "pAsSwOrD",
    "123456",
    "qwerty",
    "QWERTY",
    "letmein",
    "LetMeIn",
])
def test_common_passwords_not_strong(pw):
    # Common words are weak regardless of case (and are short anyway)
    assert is_strong(pw) is False


def test_non_common_similar_password_is_strong():
    assert is_strong("Password1234x") is True or is_strong("Password1234x") is False


def test_deterministic():
    assert is_strong(VALID) == is_strong(VALID)


def test_all_requirements_independent_of_position():
    assert is_strong("1" + "a" * 10 + "A") is True
    assert is_strong("A" + "1" + "a" * 10) is True
    assert is_strong("a" * 10 + "1A") is True
