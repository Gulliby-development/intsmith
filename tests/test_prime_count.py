import pytest

from intsmith.commands.prime import run
from intsmith.core.text import Failure


class FakeIo:
    def __init__(self) -> None:
        self.out_calls: list[str] = []

    def read_stdin(self) -> bytes:
        return b""

    def out(self, text: str) -> None:
        self.out_calls.append(text)

    def err(self, text: str) -> None:
        raise AssertionError(text)


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        (["list", "--count", "10", "30"], "primes from 10 to 30: 6\n"),
        (["list", "10", "30", "--count"], "primes from 10 to 30: 6\n"),
        (["list", "--count", "0", "1"], "primes from 0 to 1: 0\n"),
        (["list", "--count", "2", "2"], "primes from 2 to 2: 1\n"),
        (["list", "--count", "1000", "11000"], "primes from 1000 to 11000: 1167\n"),
        (["list", "10", "13"], "primes from 10 to 13: 2\n11\n13\n"),
    ],
)
def test_list_count_prints_only_the_header(argv: list[str], expected: str) -> None:
    io = FakeIo()

    assert run(argv, io) == 0
    assert io.out_calls == [expected]


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (["list", "--count", "30", "10"], "HI must not be below LO"),
        (["list", "--count", "0", "10001"], "HI - LO must be at most 10000"),
        (["list", "--count", "10"], "missing HI"),
        (["list", "--count"], "missing LO"),
        (["list", "--count", "1", "2", "3"], "too many arguments"),
        (["list", "--count=1", "1", "2"], "--count takes no value"),
        (["test", "--count", "7"], 'unknown option "--count"'),
        (["next", "--count", "7"], 'unknown option "--count"'),
        (["list", "--total", "1", "2"], 'unknown option "--total"'),
    ],
)
def test_list_count_keeps_the_list_diagnostics(argv: list[str], message: str) -> None:
    io = FakeIo()

    with pytest.raises(Failure) as exc_info:
        run(argv, io)

    assert exc_info.value.message == message
    assert io.out_calls == []
