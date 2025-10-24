import pytest

from backend.utils.validators import is_senior_title


def test_is_senior_title_positive():
    assert is_senior_title("Managing Director")
    assert is_senior_title("Head of Capital Markets")


def test_is_senior_title_negative():
    assert not is_senior_title("Marketing Specialist")
    assert not is_senior_title("Associate")
