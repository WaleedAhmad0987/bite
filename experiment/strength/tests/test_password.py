import pytest

from experiment.strength.functions.password import *


class TestIsStrong:
    def test_valid_strong_password(self):
        assert is_strong("Abcdefghij12") is True

    def test_too_short(self):
        assert is_strong("Abcdefg1") is False

    def test_exactly_eleven_chars_rejected(self):
        assert is_strong("Abcdefghi12") is False

    def test_exactly_twelve_chars_accepted(self):
        assert is_strong("Abcdefghij12") is True

    def test_empty_string(self):
        assert is_strong("") is False

    def test_missing_uppercase(self):
        assert is_strong("abcdefghij12") is False

    def test_missing_lowercase(self):
        assert is_strong("ABCDEFGHIJ12") is False

    def test_missing_digit(self):
        assert is_strong("Abcdefghijkl") is False

    def test_only_digits(self):
        assert is_strong("123456789012") is False

    def test_only_symbols(self):
        assert is_strong("!!!!!!!!!!!!") is False

    def test_long_password_accepted(self):
        assert is_strong("A1" + "b" * 100) is True

    def test_symbols_not_required(self):
        assert is_strong("Abcdefghij12") is True

    def test_symbols_allowed(self):
        assert is_strong("Abc!defghij1@") is True

    def test_spaces_allowed(self):
        assert is_strong("Abc defghij 12") is True

    @pytest.mark.parametrize("password", sorted(COMMON))
    def test_common_passwords_rejected(self, password):
        assert is_strong(password) is False

    @pytest.mark.parametrize(
        "password",
        ["Password123!", "PASSWORD123!", "QWERTY123456", "Qwerty123456", "LetMeIn12345"],
    )
    def test_common_passwords_case_insensitive(self, password):
        assert is_strong(password) is False

    def test_common_with_extra_suffix_not_blocked(self):
        assert is_strong("Password123!x") is True

    def test_common_set_contents(self):
        assert COMMON == {"password123!", "qwerty123456", "letmein12345"}

    def test_unicode_upper_lower_digit(self):
        assert is_strong("Éécdefghij12") is True

    def test_unicode_digit_counts(self):
        assert is_strong("Abcdefghij٣٤") is True

    def test_returns_bool(self):
        assert isinstance(is_strong("Abcdefghij12"), bool)
        assert isinstance(is_strong("short"), bool)
