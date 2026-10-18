import pytest

from intsmith.core.text import BIG, Failure, join_or, line, plural, show


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("A B\té", '"A?B??"'),
        ("", '""'),
        ("!~", '"!~"'),
        (" ", '"?"'),
        ("!", '"!"'),
        ("~", '"~"'),
        ("\x00\t\n", '"???"'),
        ("\x7f", '"?"'),
        ("é", '"?"'),
        ('say"hi"\\path', '"say"hi"\\path"'),
    ],
)
def test_show(text: str, expected: str) -> None:
    assert show(text) == expected


def test_failure_preserves_message() -> None:
    failure = Failure("message")
    assert failure.message == "message"


def test_big_is_twenty_nines() -> None:
    assert BIG == 99999999999999999999


@pytest.mark.parametrize(
    ("items", "expected"),
    [
        ([], ""),
        (["A"], "A"),
        (["A", "B"], "A or B"),
        (["A", "B", "C"], "A, B or C"),
        (["A", "B", "C", "D"], "A, B, C or D"),
    ],
)
def test_join_or(items: list[str], expected: str) -> None:
    assert join_or(items) == expected


@pytest.mark.parametrize(
    ("count", "one", "many", "expected"),
    [
        (1, "prime", "primes", "1 prime"),
        (0, "prime", "primes", "0 primes"),
        (2, "prime", "primes", "2 primes"),
        (-1, "congruence", "congruences", "-1 congruences"),
    ],
)
def test_plural(count: int, one: str, many: str, expected: str) -> None:
    assert plural(count, one, many) == expected


@pytest.mark.parametrize(
    ("key", "value", "expected"),
    [
        ("gcd", "2", "gcd       2\n"),
        ("bigomega", "6", "bigomega  6\n"),
        ("x", "", "x         \n"),
    ],
)
def test_line(key: str, value: str, expected: str) -> None:
    assert line(key, value) == expected
