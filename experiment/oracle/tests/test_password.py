import pytest

from experiment.oracle.functions.password import *


VALID = "Abcdefghij123"  # 13 chars, upper, lower, digit


def test_valid_strong_password():
    assert is_strong(VALID) is True


def test_empty_string():
    assert is_strong("") is False


def test_exactly_12_chars_is_too_short():
    pw = "Abcdefghij12"
    assert len(pw) == 12
    assert is_strong(pw) is False


def test_13_chars_is_long_enough():
    pw = "Abcdefghij123"
    assert len(pw) == 13
    assert is_strong(pw) is True


def test_shorter_than_12_chars():
    assert is_strong("Ab1") is False


def test_missing_uppercase():
    assert is_strong("abcdefghij123") is False


def test_missing_lowercase():
    assert is_strong("ABCDEFGHIJ123") is False


def test_missing_digit():
    assert is_strong("Abcdefghijklm") is False


def test_only_digits():
    assert is_strong("1234567890123") is False


def test_only_letters_no_digit():
    assert is_strong("AbCdEfGhIjKlMn") is False


def test_special_characters_only_not_sufficient():
    assert is_strong("!!!!!!!!!!!!!!") is False


def test_special_characters_with_all_classes_is_strong():
    assert is_strong("Abcdefghij12!@#") is True


def test_common_passwords_set_contents():
    assert COMMON == {"password123!", "qwerty123456", "letmein12345"}


def test_common_passwords_are_exactly_12_chars():
    # All entries are 12 chars, so they fail the length check first
    for pw in COMMON:
        assert len(pw) == 12
        assert is_strong(pw) is False


def test_common_password_uppercase_variant_rejected():
    assert is_strong("PASSWORD123!") is False


def test_common_password_mixed_case_variant_rejected():
    assert is_strong("Password123!") is False


def test_common_check_is_case_insensitive_when_longer(monkeypatch):
    import experiment.oracle.functions.password as mod

    monkeypatch.setattr(mod, "COMMON", {"abcdefghij123"})
    assert mod.is_strong("Abcdefghij123") is False
    assert mod.is_strong("ABCDEFGHIJ123") is False


def test_common_exact_match_rejected_when_longer(monkeypatch):
    import experiment.oracle.functions.password as mod

    monkeypatch.setattr(mod, "COMMON", {"abcdefghij123"})
    assert mod.is_strong("abcdefghij123") is False


def test_non_common_password_not_rejected_by_common_list(monkeypatch):
    import experiment.oracle.functions.password as mod

    monkeypatch.setattr(mod, "COMMON", {"somethingelse1A"})
    assert mod.is_strong(VALID) is True


def test_whitespace_counts_toward_length():
    assert is_strong("Abc1         x") is True


def test_unicode_upper_and_lower():
    assert is_strong("Éécéééééééé123") is True


def test_unicode_digit_counts_as_digit():
    # Arabic-Indic digits satisfy str.isdigit()
    assert is_strong("Abcdefghijkl\u0663") is True


def test_returns_bool():
    assert isinstance(is_strong(VALID), bool)
    assert isinstance(is_strong("short"), bool)
